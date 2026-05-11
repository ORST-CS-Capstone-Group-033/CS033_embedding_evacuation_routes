import rasterio
import numpy as np
import sys
#from osgeo import ogr

#rasterio is for terrain geotiff
#osgeo is for road datapoints

###--------------Variables---------------###

rasterXSize = 0 #how many indices per row

#test data for start and end point
start = (542410.0, 4944193.0)
end = (542430.0, 4944173.0)

#Terrain tif file data:
band = None
bounds = []
transf = rasterio.Affine(0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0)

#important changes are transf[0], transf[1], transf[3], and transf[5]

#Geotransform values:
#transf[0] = x-coordinate of the upper-left corner of the upper-left pixel.
#transf[1] = w-e pixel resolution / pixel width.
#transf[2] = row rotation (typically zero).
#transf[3] = y-coordinate of the upper-left corner of the upper-left pixel.
#transf[4] = columnn rotation (typically zero).
#transf[5] = n-s pixel resolution / pixel height (negative value for a north-up image).

road_coords = [] #stores the GPKG road coordinates

file_path = 'salem.tif' #file path to tif file
gpkg_file_path = 'testRoad.gpkg'


###-----------------ToDo-----------------###
#Create/include way to use pre-made gpkg file into code
#Create outer loop logic in main function (to itterate through all start/end coordinates for road line)



###--------------Functions---------------###

#-------Example function header-----
#Function name: 
#Parameters: 
#Description: 
#Additional notes:

#Function name: openTIF
#Parameters: file_path (path to terrain tif from current directory)
#Description: defines the global variables for band, bounds, and transf based on defined tif file
#Additional notes: N/A
def openTIF(file_path):
    global band
    global bounds
    global transf
    global rasterXSize
    with rasterio.open(file_path) as src:
        band = src.read(1)
        tempbounds = src.bounds
        #print('tempbounds = ', tempbounds) test print
        bounds = [tempbounds.left, tempbounds.bottom, tempbounds.right, tempbounds.top]
        #print('bounds: ', bounds) test print
        transf = src.transform

        rasterXSize = src.width
        print('--------------------tif file data-----------------------')
        print('band saved as: ', band)
        print('bounds saved as: ', bounds)
        print('transf saved as: ', transf)
        print('rasterXSize saved as: ', rasterXSize)
        return 1


#Function name: indiceTo2DCoord
#Parameters: indice (numbering for an indice on the terrain), rasterXSize (row depth for the terrain; how many indices per row)
#Description: Takes an indice number and converts it into a pixel coordinate value based on the terrain dimension
#Additional notes: N/A
def indiceTo2DCoord(indice, rasterXSize):
    x = indice % rasterXSize;  #row (0-9)
    y = indice // rasterXSize; #column (0,10,20)

    return np.array([x,y,0], dtype = int)


#Function name: barycentricConversion
#Parameters: pixelX (X pixel coordinate value), pixelY (Y pixel coordinate value), tri1/tri2/tri3 (pixel coordinate value for triangle vertice respective to ordering)
#Description: Calculates the STU values for a point withn the triangle based on its pixel coordinate values
#Additional notes:
def barycentricConversion(pixelX, pixelY, tri1, tri2, tri3):
    #Barycentric coord formula:
    #s*v1.z + t*v2.z+u*v3.z
    #tri1 = A, tri2 = B, tri3 = C
    #pixelX, pixelY = p
    
    #below is process from stack exchange (https://gamedev.stackexchange.com/questions/23743/whats-the-most-efficient-way-to-find-barycentric-coordinates)
    #Vector v0 = b - a, v1 = c - a, v2 = p - a;
    vec1 = np.array([tri2[0] - tri1[0], tri2[1] - tri1[1]])
    vec2 = np.array([tri3[0] - tri1[0], tri3[1] - tri1[1]])
    vec3 = np.array([pixelX - tri1[0], pixelY - tri1[1]])
    
    #use dot procduct
    dot00 = np.dot(vec1, vec1)
    dot01 = np.dot(vec1, vec2)
    dot02 = np.dot(vec1, vec3)
    dot11 = np.dot(vec2, vec2)
    dot12 = np.dot(vec2, vec3)
    
    denom = (dot00 * dot11 - dot01 * dot01)
    u = (dot00 * dot12 - dot01 * dot02) / denom
    t = (dot11 * dot02 - dot01 * dot12) / denom
    s = 1.0 - t - u
    
    return np.array([s,t,u], dtype = float)
    
    
#Function name: barycentricZVal
#Parameters: stuVal (STU values for a triangle in an array), tri1/tri2/tri3 (pixel coordinate value for triangle vertice respective to ordering)
#Description: Calculate the z-value (height) for a specific point within a triangle
#Additional notes: N/A
def barycentricZVal(stuVal, tri1, tri2, tri3):
    #use the stu values to calculate the z value at a point
    #print('testing for z val coordinates: ', tri1, tri2, tri3)

    interpVal = stuVal[0]*band[tri1[0],tri1[1]] + stuVal[1]*band[tri2[0],tri2[1]] + stuVal[2]*band[tri3[0],tri3[1]]
    #tri[2] is the z-coordinate
    
    #testing print
    #print('calculated z-val: ', interpVal)
    
    return interpVal


#Function name: findLatLonLocation
#Parameters: lat (latitude value), lon (longitudinal value), transf (geotransform data from terrain tif)
#Description: Converts a lat/lon road coordinate value into pixel coordinates. Determines which triangle within each square grid the road coordinate belongs in
#Description cont: returns the following: pixel coordinate values for the triangle's vertices, the z-value of the coordinate, and the pixel coordinate values
#Additional notes: Most of the code based on slide 3
def findLatLonLocation(lat, lon, transf):

    #print('transform: ', transf.c)
    #print('lat, lon', lat, lon)
    
    #miscomunication here, lat = world_x and lon = world_y
    pixelY = (lon - transf.f) / transf.e
    pixelX = (lat - transf.c) / transf.a

    #print('pixelX, pixelY', pixelX, pixelY)

    floorY = int(np.floor(pixelY))
    floorX = int(np.floor(pixelX))
    
    #print('floorX, floorY', floorX, floorY)

    #NOTE* these might be mapped in reverse (change later)
    tri1Indx1 = floorX + floorY * rasterXSize           #top left
    tri1Indx2 = floorX + 1 + floorY * rasterXSize       #top right
    tri1Indx3 = floorX + 1 + (floorY + 1) * rasterXSize #bottom right

    tri2Indx1 = floorX + floorY * rasterXSize           #top left
    tri2Indx2 = floorX + 1 + (floorY + 1) * rasterXSize #bottom right
    tri2Indx3 = floorX + (floorY + 1) * rasterXSize     #bottom left

    #determine if point is on top or bottom candidate using barycentric coordinates
    
    #convert indices to 2d Coords
    tri1Coord1 = indiceTo2DCoord(tri1Indx1, rasterXSize)
    tri1Coord2 = indiceTo2DCoord(tri1Indx2, rasterXSize)
    tri1Coord3 = indiceTo2DCoord(tri1Indx3, rasterXSize)
    
    tri2Coord1 = indiceTo2DCoord(tri2Indx1, rasterXSize)
    tri2Coord2 = indiceTo2DCoord(tri2Indx2, rasterXSize)
    tri2Coord3 = indiceTo2DCoord(tri2Indx3, rasterXSize)
    
    #get the stu values for each triangle
    tri1STU = barycentricConversion(pixelX, pixelY, tri1Coord1, tri1Coord2, tri1Coord3)
    tri2STU = barycentricConversion(pixelX, pixelY, tri2Coord1, tri2Coord2, tri2Coord3)
    
    #check which triangle the point is located in.
    #The barycentric coordinate in the proper triangle will result in s, t, u values between 0 and 1
    
    #testing var:
    print('--------------------lat lon to pixel coord-----------------------')
    print('tri1 STU: ', tri1STU[0], tri1STU[1], tri1STU[2])
    print('tri2 STU: ', tri2STU[0], tri2STU[1], tri2STU[2])

    print('tri1 pixel coords: ', tri1Coord1, tri1Coord2, tri1Coord3)
    print('tri2 pixel coords: ', tri2Coord1, tri2Coord2, tri2Coord3)
    
    
    if(0<=tri1STU[0]<=1 and 0<=tri1STU[1]<=1 and 0<=tri1STU[2]<=1):
        #tri1 is the valid one (top left, top right, bottom right)
        print('lat lon to pixel coord (tri1): Passed')
        return tri1Coord1, tri1Coord2, tri1Coord3, tri1STU, barycentricZVal(tri1STU, tri1Coord1, tri1Coord2, tri1Coord3), (pixelX, pixelY)
        
    
    elif(0<=tri2STU[0]<=1 and 0<=tri2STU[1]<=1 and 0<=tri2STU[2]<=1):
        #tri2 is the valid one (top left, bottom right, bottom left)
        print('lat lon to pixel coord (tri2): Passed')
        return tri2Coord1, tri2Coord2, tri2Coord3, tri2STU, barycentricZVal(tri2STU, tri2Coord1, tri2Coord2, tri2Coord3), (pixelX, pixelY)
    
    else: #this shouldn't happen
        raise RuntimeError('no valid triangle to choose from')



#Function name: findPointLocation
#Parameters: sVal/tVal/uVal (currentPoint's STU value)
#Description: Based on current point STU, determine if it's inside triangle, on triangle's edge, or on triangle's vertice
#Additional notes: eps is used as tolerance for exact values. Assume if else reaches, point is on triangle's edge
def findPointLocation(sVal, tVal, uVal):
    
    #find where on/in the triangle the current road point is
    #---
    #If all stu values are greater than 0, it's inside the triangle (outcome 1)
    #If one of the stu values == 1, then it's on one of the triangle's vertexs (outcome 2)
    #If one of the stu values == 0, then it's on the opposite side's edge from the vertex that equals 0 (outcome 3)
    
    eps = 1e-9
    
    if abs(sVal - 1.0) < eps or abs(tVal - 1.0) < eps or abs(uVal - 1.0) < eps:
        #print('point is on vertex of triangle (2)')
        return 2

    elif abs(sVal) < eps or abs(tVal) < eps or abs(uVal) < eps:
        #print('point is on edge of triangle (3)')
        return 3

    elif sVal > eps and tVal > eps and uVal > eps:
        #print('point is inside of triangle (1)')
        return 1

    else:
        print('point is numerically near boundary; treating as edge (3). Case testing STU values: ', sVal, tVal, uVal)
        return 3

#Function name: directionVector
#Parameters: currentPoint (pixel coordinate values for current point), endPoint (pixel coordinate values for end point)
#Description: using the current and end point, calculate the direction vector
#Additional notes: N/A
def directionVector(currentPoint, endPoint):
    #print("current point and endpoint: ", currentPoint, endPoint)
    d = endPoint - currentPoint
    #print('direction is: ', d)
    return d


#Function name: meshWalkFromEdge
#Parameters: tri1/tri2/tri3 (pixel coordinate value for triangle vertice respective to ordering), sVal/tVal/uVal (currentPoint's STU value), d (direction vector)
#Description: From a triangular mesh edge, find the pixel coordinates of the triangle you're heading into
#Additional notes: N/A
def meshWalkFromEdge(tri1, tri2, tri3, sVal, tVal, uVal, d):
    #This assumes egde is a non-border edge from the terrain mesh
    #From a point on an edge of a triangle, determine which triangle the line is pointing assuming direction vector d
    #This will use ray-casting

    tri1 = np.array(tri1[:2], dtype=float)
    tri2 = np.array(tri2[:2], dtype=float)
    tri3 = np.array(tri3[:2], dtype=float)
    
    eps = 1e-9

    print('----Calculated variables from within meshWalkFromEdge:')
    
    #Determine which edge of the triangle the current point is on
    if(abs(sVal) < eps):
        #edge is made of t and u val
        print('sVal is 0; edge is made of t and u')
        edge = tri3 - tri2
        O_A = tri1
        e1 = tri2
        e2 = tri3
        
    elif(abs(tVal) < eps):
        #edge is made from s and u val
        print('tVal is 0; edge is made of s and u')
        edge = tri3 - tri1
        O_A = tri2
        e1 = tri1
        e2 = tri3

    elif(abs(uVal) < eps):
        #edge is made from s and t val
        print('uVal is 0; edge is made of s and t')
        edge = tri2 - tri1
        O_A = tri3
        e1 = tri1
        e2 = tri2
        
    else: 
        raise RuntimeError(f"Point is not on an edge: s={sVal}, t={tVal}, u={uVal}")
    

    #Using known edge, determine which vertice is unkown and define it as O_B (find O_B pixel coordinates)
    if(e2[0]==e1[0]):
        #edge is vertical
        print('EDGE IS VERTICAL (x=x)')
        if(O_A[0] < e1[0]): #bottom right is O_B
            O_B = np.array([e1[0]+1, O_A[1]+1])
        else: #top left is O_B
            O_B = np.array([e1[0]-1, O_A[1]-1])
        
    elif(e2[1]==e1[1]):
        #edge is horizontal
        print('EDGE IS HORIZONTAL (y=y)')
        if(O_A[1] < e1[1]):#bottom right is O_B
            O_B = np.array([O_A[0]+1, e1[1]+1])
        else:#top left
            O_B = np.array([O_A[0]-1, e1[1]-1])
            
    else:
        #edge is diagnol
        print('EDGE IS DIAGNOL (x!=x and y!=y)')
        
        #Need to make sure we know if e1 is top left or bottom right
        if(e1[0] > e2[0] and e1[1] > e2[1]):
            #e1 is bottom right
            if(O_A[0] == e1[0] and O_A[1] == e2[1]):#bottom left is O_B
                O_B = np.array([O_A[0]-1, O_A[1]+1])
            else:#top right
                O_B = np.array([O_A[0]+1, O_A[1]-1])
        else:
            #e2 is bottom right
            if(O_A[0] == e1[0] and O_A[1] == e2[1]):#top right is O_B
                O_B = np.array([O_A[0]+1, O_A[1]-1])
            else:#bottom left
                O_B = np.array([O_A[0]-1, O_A[1]+1])
         
    #Test prints:
    print('Non-edge (initially known) vertice O_A ', O_A)
    print('Non-edge (initially unknown) vertice O_B ', O_B)
    print('Edge vertices (e1, e2): ', e1, e2)        
    print('Edge is (e2 - e1): ', edge)
    
    #calculate perpendicular from edge
    perp = np.array([edge[1], -edge[0]])
    print('Perpendicular is:', perp)
    
    #take dot products to find which triangle the path goes into
    dot_O_A = np.dot(O_A - e1, perp)
    dot_O_B = np.dot(O_B - e1, perp)
    ray = np.dot(d, perp)
        
    #More test prints:
    print('calculated dot_O_A and dot_O_B: ', dot_O_A, dot_O_B)
    print('Final results (valid expects result to be greater than 0):')
    print('dot_o_a_ray is: ', (ray*dot_O_A))
    print('dot_o_b_ray is: ', (ray*dot_O_B))
    
    #return O_A or O_B depending on which direction road is heading into
    if(ray*dot_O_A > 0):
        #heading into triangle with O_A
        print('Heading into triangle with O_A... ray is:', ray)
        print('----End calculations from within meshWalkFromEdge')
        return np.array([e1, e2, O_A])
    elif(ray*dot_O_B > 0):
        #heading into triangle with O_B
        print('Heading into triangle with O_B... ray is:', ray)
        print('----End calculations from within meshWalkFromEdge')
        return np.array([e1, e2, O_B])
    else: 
        raise RuntimeError('meshWalkFromEdge: no valid triangles found')


#Function name: det
#Parameters: a/b (two placeholder variables used in the determinantCalculator, depending on which, can be direction vector or edge)
#Description: calculate the determinant of an edge using direction vector
#Additional notes: Only used in determinantCalculator
def det(a, b):
    return a[0] * b[1] - a[1] * b[0]


#Function name: determinantCalculator
#Parameters: d (direction vector), edge1 (Left-side edge connected to a vertice), edge2 (Right-side edge connected to a vertice)
#Description: Determine if a direction vector is between two edges of an adjacent triangle (current point is on a vertice)
#Additional notes: The final if statement depends on which direction x and y are positive in. If y down is negative, flip the less than sign to greater than
def determinantCalculator(d, edge1, edge2):
    #additional safeguard check
    if(det(edge1,edge2) < 0.0):
        print("flipped edge1 and edge2")
        temp = edge2
        edge1 = edge2
        edge2 = temp
    
    det0 = det(d, edge1)
    det1 = det(edge2, d)
    
    if(det0 <= 0 and det1 < 0):
        print("Determinant calculation passed, det0 and det1 results are as follows: ", det0, det1)
        if(det0 == 0):
            print('Direction is colinear')
            return 2
        else: 
            print('Direction isnt colinear')
            return 1
    #direction of next triangle is not within edges, try again
    return 0
    

#Function name: meshWalkFromVertex
#Parameters: d (direction vector)
#Description: Determine the direction (compared to the starting vertex) of the two edges that constrain the direction vector
#Additional notes: will return the direction from the current vertex the two additional triangle points will be. To get a pixel coordinate value, additional code will be required
def meshWalkFromVertex(d):
    #determine which of the 6 adjacent triangles the path goes into
    
    #Assuming visuals are the same as slides:
    #Triangle 1: edge 1 + edge 2
    #Triangle 2: edge 2 + edge 5
    #Triangle 3: edge 5 + edge 8
    #Triangle 4: edge 8 + edge 7
    #Triangle 5: edge 7 + edge 4
    #Triangle 6: edge 4 + edge 1
    
    #prod 0 = det(dir vector, first edge)
    #prod 1 = det(second edge, dir vector)
    
    #calculate edge direction vector
    #edge1 = startDir - 1
    #edge2 = startDir[1] - 1
    #edge4 = startDir[0] - 1
    #edge5 = startDir[0] + 1
    #edge7 = startDir[1] + 1
    #edge8 = startDir + 1
    
    edge1 = np.array([-1, -1]) #up left
    edge2 = np.array([0, -1]) #up
    edge4 = np.array([-1, 0]) #left
    edge5 = np.array([1, 0]) #right
    edge7 = np.array([0, 1]) #down
    edge8 = np.array([1, 1]) #down right

    #Test prints:
    print('----Calculated variables from within meshWalkFromVertex:')
    
    print(f"DIRECTION: ", d)
    print("Determinant of edge1 and edge2: ", determinantCalculator(d, edge1, edge2))
    print("Determinant of edge2 and edge5: ", determinantCalculator(d, edge2, edge5))
    print("Determinant of edge5 and edge8: ", determinantCalculator(d, edge5, edge8))
    print("Determinant of edge8 and edge7: ", determinantCalculator(d, edge8, edge7))
    print("Determinant of edge7 and edge4: ", determinantCalculator(d, edge7, edge4))
    
    #check each triangle until prod0 >= 0 and prod1 > 0    
    #determinantCalculator function will return var depending on the following:
    #return 0 if !prod0 >= 0 or !prod1 > 0
    #return 1 if prod0 >= 0 and prod1 > 0 but not colinear (prod0 !== 0)
    #return 2 if prod0 == 0 and prod1 > 0 (colinear)
    
    #for now, just return a specific number based on which triangle is valid
    if determinantCalculator(d, edge1, edge2):
        print('Calculated that next triangle is between edge1 and edge2')
        return np.array([edge1, edge2])
    elif determinantCalculator(d, edge2, edge5):
        print('Calculated that next triangle is between edge2 and edge5')
        return np.array([edge2, edge5])
    elif determinantCalculator(d, edge5, edge8):
        print('Calculated that next triangle is between edge5 and edge8')
        return np.array([edge5, edge8])
    elif determinantCalculator(d, edge8, edge7):
        print('Calculated that next triangle is between edge8 and edge7')
        return np.array([edge8, edge7])
    elif determinantCalculator(d, edge7, edge4):
        print('Calculated that next triangle is between edge7 and edge4')
        return np.array([edge7, edge4])
    elif determinantCalculator(d, edge4, edge1):
        print('Calculated that next triangle is between edge4 and edge1')
        return np.array([edge4, edge1])
    else:
        print("there was a problem in the meshwalkfromvertex function, couldn't find valid triangle")
        

#Function name: findNextTriangleEdge
#Parameters: p (currentPoint in pixel coordinates), triCoords (pixel coordinates of triangle vertices), dir (direction vector)
#Description: Determine which edge of the triangle will be intersected and the pixel coordinate of where the intersection will happen
#Additional notes:
def findNextTriangleEdge(p, triCoords, dir):
    #Ray: r(t) = p + t * dir where t > 0
    #Edge: e(u) = e0 + ue where  0 <= u <= 1 and e = e1 - e0
    
    #p = current point (2d)
    #t = a scalar defined in the calculation below where:
    #e0 = first point on the edge
    #e = second point on your edge minus your first point (e1 – e0, a vector)
    #dir = direction vector
    #u = a scalar like t which must be between 0 and 1

    print('----Calculated variables from within findNextTriangleEdge:')

    vert0 = np.array(triCoords[0][:2], dtype=float)
    vert1 = np.array(triCoords[1][:2], dtype=float)
    vert2 = np.array(triCoords[2][:2], dtype=float)
    
    edges = [
        (vert0, vert1),
        (vert1, vert2),
        (vert2, vert0),
    ]

    print('p (current 2d point): ', p)
    print('vertice coordinates in triangle: ', triCoords)
    
    eps = 1e-9
   
    #do these calculations for each edge where t > 0 and 0 <= u <= 1
    for e0, e1 in edges:
        e = e1 - e0
        denom = det(dir, e)
        
        diff = e0 - p
        t = det(diff, e) / denom
        u = det(diff, dir) / denom
        
        print("checking edge: ", e0, e1)
        print("t: ", t, "u: ", u)
        
        if t > eps and (0-eps) <= u <= (1+eps):
            nextPoint = p + t * dir
            print('nextPoint is: ', nextPoint)
            print('----End calculations from within findNextTriangleEdge')
            return nextPoint
    
    #Of the three edges, none passed (this shouldn't happen)
    raise RuntimeError("No valid next edge intersection found")
    


###--------------Main Function---------------###

if __name__ == "__main__":
    openTIF(file_path)
    print('Save tif variables: Passed')
    #Saving road coordinate values using gpkg would go here
    #print('Save gpkg variables: Passed')


    #------------------------------------Outside loop logic goes here:-------------------------------------

    #Needs to: choose a start and end point based on road coordinate array
    #Calculate the initial values to use within the inner loop (this part is done)

    #Get and read road coordinate array:

    #Choose start/end value to use

    #add stuff here


    #Get initial pixel coordinate values from start/finish coordinates

    triStartCoord1, triStartCoord2, triStartCoord3, tri1STU, startZval, pixelCoordStart = findLatLonLocation(start[0], start[1], transf)
    triEndCoord1, triEndCoord2, triEndCoord3, tri2STU, endZval, pixelCoordEnd = findLatLonLocation(end[0], end[1], transf)

    #print initial values for triangle's vertice pixel coords
    print('--------------------initial calculated values-----------------------')
    print('current start triangle points: ', triStartCoord1, triStartCoord2, triStartCoord3)
    print('current end triangle points: ', triEndCoord1, triEndCoord2, triEndCoord3)
    print('pixelCoord start value: ', pixelCoordStart)
    print('pixelCoord end value: ', pixelCoordEnd)

    #print current start/end z-values at start/end points
    print('start z value: ', startZval)
    print('end z value: ', endZval)
    print('Calculate initial values: Passed')

    #Determine if point is on triangle inside, edge, or vertice
    pointLocationVar = findPointLocation(tri1STU[0], tri1STU[1], tri1STU[2])

    #Define initial currentPoint, endPoint, and direction vector
    colinearVal = 0 #0 means not colinear, 1 means colinear
    currentPoint = np.array(pixelCoordStart, dtype=float)
    endPoint = np.array(pixelCoordEnd, dtype=float)
    dir = directionVector(currentPoint, endPoint)

    #testing array to store walked points:
    walkedPoints = []

    #Update triCoords value based on where within the triangle currentPoint is
    print('--------------------initial current triangle calculations-----------------------')

    if(pointLocationVar == 1):#point is within the triangle
        triCoords = np.array([triStartCoord1, triStartCoord2, triStartCoord3])
        print('finished calculating triCoords for point within triangle')
        
    elif(pointLocationVar == 2):#point is on one of the triangle's vertices
        edgePair = meshWalkFromVertex(dir)

        tempCoord1 = edgePair[0]
        tempCoord2 = edgePair[1]
        
        newCoord1 = np.array([tempCoord1[0] + currentPoint[0], tempCoord1[1] + currentPoint[1]])
        newCoord2 = np.array([tempCoord2[0] + currentPoint[0], tempCoord2[1] + currentPoint[1]])
        
        #print("new coords from vertice are: ", newCoord1, newCoord2)
        
        triCoords = np.array([newCoord1, newCoord2, currentPoint])
        print('----End calculations from within meshWalkFromVertex')
        
        #IMPORTANT: ADD COLINEAR DETECTION FUNCTION HERE

        print('finished calculating triCoords for point on triangle vertice')
        
    elif(pointLocationVar == 3):#point is on one of the triangle's edges
        triCoords = meshWalkFromEdge(triStartCoord1, triStartCoord2, triStartCoord3, tri1STU[0], tri1STU[1], tri1STU[2], dir) #assume direction vector d
        print('finished calculating triCoords for point on triangle edge')

    print('initial saved triCoords value: ', triCoords)
    print('Calculate outer loop initial variables: Passed')



    #------------------------------------Inside loop logic goes here:--------------------------------------
    #Step 1: Based on knowing which triangle you're heading into, find the edge/vertice that will be intersected

    endLoop = False
    failSafe = 0

    while not endLoop:
        failSafe += 1
        if(failSafe == 100):
            print('failSafe activated')
            break
        
        print('--------------------inner loop connector calculation ', failSafe,'-----------------------')

        #check if end point is within current triangle
        endSTU = barycentricConversion(pixelCoordEnd[0], pixelCoordEnd[1], triCoords[0], triCoords[1], triCoords[2])

        if(0 <= endSTU[0] <= 1 and 0 <= endSTU[1] <= 1 and 0 <= endSTU[2] <= 1):
            print('end is inside next triangle')
            print('inner loop functionality: Passed')
            endLoop = True
            break #delete this after testing---------------
        else:
            print('-End is not inside next triangle, continuing loop-')

        #check if direction is colinear
        if(colinearVal == 1):
            #colinear, change values so error doesn't occur in finding next edge
            print('current point is colinear')
        else:
            #end is not within next triangle so update direction vector and currentPoint 
            #print('end point is NOT colinear')
            dir = directionVector(np.array(currentPoint, dtype=float), np.array(pixelCoordEnd, dtype=float))
            currentPoint = findNextTriangleEdge(currentPoint, triCoords, dir)
 
        
        #Step 2: Find vertice coordinates of next triangle (triCoords)
        print('currentPoint: ', currentPoint)
        triCoordsSTU = barycentricConversion(currentPoint[0], currentPoint[1], triCoords[0], triCoords[1], triCoords[2])
        pointLocationVar = findPointLocation(triCoordsSTU[0], triCoordsSTU[1], triCoordsSTU[2])

        if(pointLocationVar == 1):
            #This should not be possible at this point. Raise error if this happens
            raise RuntimeError('Point is inside triangle when it should be on edge/vertice')
            
        elif(pointLocationVar == 2):
            #point is walking from vertex of triangle to edge of triangle
            print('Point location variable: ', pointLocationVar, '. Point is on a vertice')
            edgePair = meshWalkFromVertex(dir)
        
            #edge pair coords are saved as translations based on current point (-1, -1) means upper left from vertice
            #use edge pair results to make the two additional pixelCoords
            
            tempCoord1 = edgePair[0]
            tempCoord2 = edgePair[1]
            
            newCoord1 = np.array([tempCoord1[0] + currentPoint[0], tempCoord1[1] + currentPoint[1]])
            newCoord2 = np.array([tempCoord2[0] + currentPoint[0], tempCoord2[1] + currentPoint[1]])
            
            #print("new coords from vertice are: ", newCoord1, newCoord2)
            
            triCoords = np.array([newCoord1, newCoord2, currentPoint])
            print('----End calculations from within meshWalkFromVertex')

            #Potentially, calculate if direction is colinear here

            walkedPoints.append(np.array([currentPoint[0], currentPoint[1], 0.0], dtype=float))
                
        elif(pointLocationVar == 3):
            #point is walking from edge of triangle to edge of triangle
            print('Point location variable: ', pointLocationVar, '. Point is on an edge')
            triCoords = meshWalkFromEdge(triCoords[0], triCoords[1], triCoords[2], triCoordsSTU[0], triCoordsSTU[1], triCoordsSTU[2], dir) #assume direction vector d
            
            #testing array to store points:
            walkedPoints.append(np.array([currentPoint[0], currentPoint[1], 0.0], dtype=float))


        print('updated triCoords value:', triCoords)
        print('End loop itteration')


    print('-------------Calculations end here-------------------')

    print('Coordinate Connectors: ')
    for i, coords in enumerate(walkedPoints):
        print('coordinate number: ', i + 1)
        print('coordinate value: ', coords[0], coords[1])
        world_x, world_y = rasterio.transform.xy(transf, coords[1], coords[0], offset='ul') #print in terms of world coords
        print('world coords:' , world_x.item(), world_y.item())



