import rasterio
import sys
import os
import numpy as np
#from osgeo import ogr

###------------Variables---------------###

#important changes are transf[0], transf[1], transf[3], and transf[5]

rasterXSize = 103 #how many indices per row

start = (542410.0, 4944193.0)
end = (542430.0, 4944173.0)

#data from tif file about terrain
band = None
bounds = []
transf = rasterio.Affine(0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0)

road_coords = [] #stores the GPKG road coordinates

file_path = 'salem.tif' #file path to tif file
gpkg_file_path = 'testRoad.gpkg'

###------------Functions---------------###

#open tif file and save band and bounds vairable types
def openTIF(file_path):
    global band
    global bounds
    global transf
    with rasterio.open(file_path) as src:
        band = src.read(1)
        tempbounds = src.bounds
        #print('tempbounds = ', tempbounds)
        bounds = [tempbounds.left, tempbounds.bottom, tempbounds.right, tempbounds.top]
        #print('bounds: ', bounds)
        transf = src.transform
        return 1


#open the gpkg (road data) file and read the road coordinates
def readGPKG(gpkg_file_path):
    global bounds #get bounds from global variable

    datasource = ogr.Open(gpkg_file_path, 0)

    layer = datasource.GetLayerByName("lines")
    if layer is None:
        print('ERROR: GPKG Data layer is None')
    
    #unsure if linear_ring has any purpose from Ziv code so I removed it
    layer.SetSpatialFilterRect(*bounds)

    layer.ResetReading()

    for feature in layer:
        geom = feature.GetGeometryRef()

        if geom is not None and geom.GetGeometryName == 'LINESTRING':
            tempcoords = []
            for p in range(geom.GetPointCount()):
                tempcoords.append((geom.GetX(p), geom.GetY(p)))
            road_coords.append(tempcoords)

    #road_coords is global but return for testing of most recent change
    return road_coords


#turns indice num (i.e. 28) into 2d coordinate (
def indiceTo2DCoord(indice, rasterXSize):
    x = indice % rasterXSize;  #row (0-9)
    y = indice // rasterXSize; #column (0,10,20)
    
    return np.array([x,y,0], dtype = int)


#slide 3 code function
def findLatLonLocation(lat, lon, transf):

    print('transform: ', transf.c)
    print('lat, lon', lat, lon)
    
    pixelY = (lon - transf.f) / transf.e
    pixelX = (lat - transf.c) / transf.a

    print('pixelX, pixelY', pixelX, pixelY)

    #floor both pixels
    floorY = int(np.floor(pixelY))
    floorX = int(np.floor(pixelX))
    
    print('floorX, floorY', floorX, floorY)

    #NOTE* these might be mapped in reverse (change later)
    tri1Indx1 = floorX + floorY * rasterXSize           #top left
    tri1Indx2 = floorX + 1 + floorY * rasterXSize       #top right
    tri1Indx3 = floorX + 1 + (floorY + 1) * rasterXSize #bottom right

    tri2Indx1 = floorX + floorY * rasterXSize           #top left
    tri2Indx2 = floorX + 1 + (floorY + 1) * rasterXSize #bottom right
    tri2Indx3 = floorX + (floorY + 1) * rasterXSize     #bottom left

    #Now we have two candidate triangles the point could be on

    #determine if point is on top or bottom candidate
    #using barycentric coordinates
    
    #first, convert indices to 2d Coords
    tri1Coord1 = indiceTo2DCoord(tri1Indx1, rasterXSize)
    tri1Coord2 = indiceTo2DCoord(tri1Indx2, rasterXSize)
    tri1Coord3 = indiceTo2DCoord(tri1Indx3, rasterXSize)
    
    tri2Coord1 = indiceTo2DCoord(tri2Indx1, rasterXSize)
    tri2Coord2 = indiceTo2DCoord(tri2Indx2, rasterXSize)
    tri2Coord3 = indiceTo2DCoord(tri2Indx3, rasterXSize)
    #then test which triangle it's in based on 2d coords
    
    tri1STU = barycentricConversion(pixelX, pixelY, tri1Coord1, tri1Coord2, tri1Coord3)
    tri2STU = barycentricConversion(pixelX, pixelY, tri2Coord1, tri2Coord2, tri2Coord3)
    
    #check which triangle the point is located in.
    #The barycentric coordinate in the proper triangle will result in s, t, u values between 0 and 1
    
    #testing var:
    print('tri1 STU: ', tri1STU[0], tri1STU[1], tri1STU[2])
    print('tri2 STU: ', tri2STU[0], tri2STU[1], tri2STU[2])

    print('tri1 pixel coords: ', tri1Coord1, tri1Coord2, tri1Coord3)
    print('tri2 pixel coords: ', tri2Coord1, tri2Coord2, tri2Coord3)
    
    
    if(0<=tri1STU[0]<=1 and 0<=tri1STU[1]<=1 and 0<=tri1STU[2]<=1):
        #tri1 is the valid one (top left, top right, bottom right)
        print('tri1 is valid')
        return tri1Coord1, tri1Coord2, tri1Coord3, tri1STU, barycentricZVal(tri1STU, tri1Coord1, tri1Coord2, tri1Coord3), (pixelX, pixelY)
        
    
    elif(0<=tri2STU[0]<=1 and 0<=tri2STU[1]<=1 and 0<=tri2STU[2]<=1):
        #tri2 is the valid one (top left, bottom right, bottom left)
        print('tri2 is valid')    
        return tri2Coord1, tri2Coord2, tri2Coord3, tri2STU, barycentricZVal(tri2STU, tri2Coord1, tri2Coord2, tri2Coord3), (pixelX, pixelY)
    
    else:
        raise RuntimeError('no valid triangle to choose from')
        #return
    


#function that determines (s,t,u) values for a point on the triangle
#aka, slide 4 code function (or lines 145 in ThreeDMesh)
def barycentricConversion(pixelX, pixelY, tri1, tri2, tri3):
    #input is pixelX, pixelY, and 3 2d points of the triangle
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
    
    
#side function that just calculates zvalue of a point using barycentric coords
def barycentricZVal(stuVal, tri1, tri2, tri3):
    #use the stu values to calculate the z value at a point
    print('testing for z val coordinates: ', tri1, tri2, tri3)
    interpVal = stuVal[0]*band[tri1[0],tri1[1]] + stuVal[1]*band[tri2[0],tri2[1]] + stuVal[2]*band[tri3[0],tri3[1]]
    #tri[2] is the z-coordinate
    
    #testing print
    print('calculated z-val: ', interpVal)
    
    return interpVal


def normalizeVector(inputVector):
    sN = inputVector / np.sqrt(np.sum(inputVector**2))
    return sN


#code for edge/vertice/inside here--------------------------------------------------------------------------------------

def findPointLocation(sVal, tVal, uVal):
    
    #find where on/in the triangle the current road point is
    #---
    #If all stu values are greater than 0, it's inside the triangle (outcome 1)
    #If one of the stu values == 1, then it's on one of the triangle's vertexs (outcome 2)
    #If one of the stu values == 0, then it's on the opposite side's edge from the vertex that equals 0 (outcome 3)
    
    eps = 1e-9
    
    if abs(sVal - 1.0) < eps or abs(tVal - 1.0) < eps or abs(uVal - 1.0) < eps:
        print('point is on vertex of triangle (2)')
        return 2

    elif abs(sVal) < eps or abs(tVal) < eps or abs(uVal) < eps:
        print('point is on edge of triangle (3)')
        return 3

    elif sVal > eps and tVal > eps and uVal > eps:
        print('point is inside of triangle (1)')
        return 1

    else:
        print('point is numerically near boundary; treating as edge (3)')
        return 3
        
        
        

def directionVector(currentPoint, endPoint):
    #basic function to get direction vector
    d = endPoint - currentPoint
    print('direction is: ', d)
    return d



def meshWalkFromEdge(tri1, tri2, tri3, sVal, tVal, uVal, d):
    #This assumes egde is a non-border edge from the terrain mesh
    #From a point on an edge of a triangle, determine which triangle the line is pointing assuming direction vector d
    #This will use ray-casting
    
    #Assume direction = d
    
    tri1 = np.array(tri1[:2], dtype=float)
    tri2 = np.array(tri2[:2], dtype=float)
    tri3 = np.array(tri3[:2], dtype=float)
    
   
    print('triangle is made of following points MESHWALKFROMEDGE: ', tri1, tri2, tri3)
    
    eps = 1e-9
    
    #-------Get edge value, O_A, and e1 based on which stu val equals 0--------
    if(abs(sVal) < eps):
        #edge is made of t and u val
        print('sVal is 0')
        edge = tri3 - tri2
        O_A = tri1
        e1 = tri2
        e2 = tri3
        
    elif(abs(tVal) < eps):
        #edge is made from s and u val
        print('tVal is 0')
        edge = tri3 - tri1
        O_A = tri2
        e1 = tri1
        e2 = tri3

    elif(abs(uVal) < eps):
        #edge is made from s and t val
        print('uVal is 0')
        edge = tri2 - tri1
        O_A = tri3
        e1 = tri1
        e2 = tri2
        
    else: 
        raise RuntimeError(f"Point is not on an edge: s={sVal}, t={tVal}, u={uVal}")
    
    #Note-unsure on how to determine O_B (other vertex for triangle 2). Ask Ziv later
    #After talking to Ziv, way to get O_B is by knowing what O_A is and getting the opposite
    #Opposite is calculated by knowing which two points make up the edge (if horizontal edge, flip y axis, if veritcal edge, flip horizontal, if diagnol edge, flip both.
    
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
        if(O_A[0] == e1[0] and O_A[1] == e2[1]):#top right is O_B
            O_B = np.array([O_A[0]+1, O_A[1]-1])
        else:#bottom left
            O_B = np.array([O_A[0]-1, O_A[1]+1])
         
    print('O_A ', O_A)
    print('O_B ', O_B)
    
    print('e1 ', e1)
    print('e2 ', e2)
    if(e1[0] == e2[0]): #horizontal edge
        print('e[0] is equal')
    elif(e1[1] == e2[1]): #vertical edge
        print('e[1] is equal')
    else: #diagonal edge
        print('neither e[0] or e[1] are equal')
        
        
        
    print('edge is: ', edge) #test... delete later
    
    #-----calculate perpendicular from edge-----
    perp = np.array([edge[1], -edge[0]])
    print('perp is:', perp)
    
    #----take dot products to find which triangle the path goes into----
    dot_O_A = np.dot(O_A - e1, perp)
    dot_O_B = np.dot(O_B - e1, perp)
    ray = np.dot(d, perp)
        
    #----Return O_A or O_B depending on which direction road is heading into-----
    print('ray is: ', ray)
    print('dot_o_a is: ', dot_O_A)
    print('dot_o_a_ray is: ', (ray*dot_O_A))
    #print('dot_o_b is: ', (ray*dot_O_B))
    
    
    if(ray*dot_O_A > 0):
        #heading into triangle with O_A
        print('O_A... ray is:', ray)
        return np.array([e1, e2, O_A])
    else:
        #heading into triangle with O_B
        print('O_B... ray is:', ray)
        return np.array([e1, e2, O_B])
        

def determinantCalculator(prod0, prod1):
    prod0Det = np.linalg.det(prod0)
    prod1Det = np.linalg.det(prod1)
    if( prod0Det >= 0 and prod1Det > 0):
        if( prod0Det == 0):
            #direction is colinear to edge
            print('direction is colinear')
            return 2
        else: 
            return 1
    return 0
    




def meshWalkFromVertex():
    #determine which of the 6 adjacent triangles the path goes into
    
    #Assuming visuals are the same as slides:
    #Triangle 1: edge 1 + edge 2
    #Triangle 2: edge 2 + edge 5
    #Triangle 3: edge 5 + edge 8
    #Triangle 4: edge 8 + edge 7
    #Triangle 5: edge 7 + edge 4
    #Triangle 6: edge 4 + edge 1
    
    #prod 0 = det( dir vector, first edge)
    #prod 1 = det( second edge, dir vector)
    
    #get 2d direction vector
    startDir = np.array(start[:2])
    endDir = np.array(end[:2])
    d = directionVector(startDir, endDir)
    
    
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
    
    
    
    #check each triangle until prod0 >= 0 and prod1 > 0    
    #determinantCalculator function will return var depending on the following:
    #return 0 if !prod0 >= 0 or !prod1 > 0
    #return 1 if prod0 >= 0 and prod1 > 0 but not colinear (prod0 !== 0)
    #return 2 if prod0 == 0 and prod1 > 0 (colinear)
    
    #for now, just return a specific number based on which triangle is valid
    
    if( determinantCalculator(np.array([d, edge1]), np.array([edge2, d])) != 0):
        print('edge1 and edge2')
        return np.array([edge1, edge2])
    elif( determinantCalculator(np.array([d, edge2]), np.array([edge5, d])) != 0):
        print('edge2 and edge5')
        return np.array([edge2, edge5])
    elif( determinantCalculator(np.array([d, edge5]), np.array([edge8, d])) != 0):
        print('edge5 and edge8')
        return np.array([edge5, edge8])
    elif( determinantCalculator(np.array([d, edge8]), np.array([edge7, d])) != 0):
        print('edge8 and edge7')
        return np.array([edge8, edge7])
    elif( determinantCalculator(np.array([d, edge7]), np.array([edge4, d])) != 0):
        print('edge7 and edge4')
        return np.array([edge7, edge4])
    elif( determinantCalculator(np.array([d, edge4]), np.array([edge1, d])) != 0):
        print('edge4 and edge1')
        return np.array([edge4, edge1])


def det2(a, b): #test function
    return a[0] * b[1] - a[1] * b[0]
    
    
def findNextTriangleEdge(p, triCoords, dir):
    #Ray: r(t) = p + t * dir where t > 0
    #Edge: e(u) = e0 + ue where  0 <= u <= 1 and e = e1 - e0
    
    #p = current point (2d)
    #t = a scalar defined in the calculation below where:
    #e0 = first point on the edge
    #e = second point on your edge minus your first point (e1 – e0, a vector)
    #dir = direction vector
    #u = a scalar like t which must be between 0 and 1

    vert0 = np.array(triCoords[0][:2], dtype=float)
    vert1 = np.array(triCoords[1][:2], dtype=float)
    vert2 = np.array(triCoords[2][:2], dtype=float)
    
    edges = [
        (vert0, vert1),
        (vert1, vert2),
        (vert2, vert0),
    ]
    
    print('preliminary values are as follows: ')
    print('p (current 2d point): ', p)
    print('vertice coordinates in triangle: ', triCoords)
    
    
    #-----test
    eps = 1e-9
    
    for e0, e1 in edges:
        e = e1 - e0
        denom = det2(dir, e)
        
        diff = e0 - p
        t = det2(diff, e) / denom
        u = det2(diff, dir) / denom
        
        print("checking edge: ", e0, e1)
        print("t: ", t, "u: ", u)
        
        if t > eps and -eps <= u <= 1 + eps:
            nextPoint = p + t * dir
            print('nextPoint is: ', nextPoint)
            return nextPoint
            
    
    #------testEnd
    

    
    #t = det(e0-p, e)/det(dir, e)
    #u = det(e0-p, dir)/det(dir, e)
    
    #do these calculations for each edge where t > 0 and 0 <= u <= 1
    #if it reaches here, fail because it shouldn't
    
    raise RuntimeError("No valid next edge intersection found")

#edge/vertice/inside case code ends here------------------------------------------------------------------







if __name__ == "__main__":
    openTIF(file_path)

    print('band test, band[2,2] is', band[2,2])

    triStartCoord1, triStartCoord2, triStartCoord3, tri1STU, startZval, pixelCoordStart = findLatLonLocation(start[0], start[1], transf)
    triEndCoord1, triEndCoord2, triEndCoord3, tri2STU, endZval, pixelCoordEnd = findLatLonLocation(end[0], end[1], transf)

    #current values:
    #print current triangle indice locations:
    print('current start triangle points: ', triStartCoord1, triStartCoord2, triStartCoord3)
    print('current end triangle points: ', triEndCoord1, triEndCoord2, triEndCoord3)
    #print current start/end z-values at start/end points
    print('start z value: ', startZval)
    print('end z value: ', endZval)
    print('pixelCoord value: ', pixelCoordStart)


    #-----------------------------------------------------------------------------------

    pointLocationVar = findPointLocation(tri1STU[0], tri1STU[1], tri1STU[2])


    #Step 1: find triangle heading into (three vertex for triangle)
    colinearVal = 0 #0 means not colinear, 1 means colinear
    currentPoint = np.array(pixelCoordStart, dtype=float)
    endPoint = np.array(pixelCoordEnd, dtype=float)
    dir = directionVector(currentPoint, endPoint)

    #testing array to store walked points:
    walkedPoints = []



    if(pointLocationVar == 1):
        #point is walking from point in triangle to an edge
        print('1->2')
        triCoords = np.array([triStartCoord1, triStartCoord2, triStartCoord3])
        
        
    elif(pointLocationVar == 2):
        #point is walking from vertex of triangle to edge of triangle
        print('2->2')
        edgePair = meshWalkFromVertex()
        print('edge pair from vertex is: ', edgePair)
        
        if(np.linalg.det(d, edgePair[0]) == 0):
            #colinear
            colinearVal = 1
        else:
            colinearVal = 0
            
        
    elif(pointLocationVar == 3):
        #point is walking from edge of triangle to edge of triangle
        print('3->2')
        triCoords = meshWalkFromEdge(triStartCoord1, triStartCoord2, triStartCoord3, tri1STU[0], tri1STU[1], tri1STU[2], dir) #assume direction vector d



    #Step 2: find edge your itterating through for triangle you're heading into
    #Loop logic starts here

    endLoop = False
    print('triCoords is: ', triCoords)
    failSafe = 0

    while not endLoop:
        failSafe += 1
        if(failSafe == 100):
            print('failSafe activated')
            break
        
        endSTU = barycentricConversion(pixelCoordEnd[0], pixelCoordEnd[1], triCoords[0], triCoords[1], triCoords[2])

        if(0 <= endSTU[0] <= 1 and 0 <= endSTU[1] <= 1 and 0 <= endSTU[2] <= 1):
            print('end is inside next triangle')
            endLoop = True
            break #delete this after testing---------------

        else:
            print('end is not inside next triangle, continuing loop')


        if(colinearVal == 1):
            #colinear, so connext point to next vertice
            print('current point is colinear')
        else:
            print('end point is NOT colinear')
            dir = directionVector(np.array(currentPoint, dtype=float), np.array(pixelCoordEnd, dtype=float))
            currentPoint = findNextTriangleEdge(currentPoint, triCoords, dir)

        
        
        
        
        
        
        #Step 3: find vertice coordinates of next triangle again
        print('currentPoint: ', currentPoint)
        triCoordsSTU = barycentricConversion(currentPoint[0], currentPoint[1], triCoords[0], triCoords[1], triCoords[2])
        pointLocationVar = findPointLocation(triCoordsSTU[0], triCoordsSTU[1], triCoordsSTU[2])

        if(pointLocationVar == 1):
            #This should not be possible at this point
            print('error, point is inside triangle at step 3')
            
        elif(pointLocationVar == 2):
            #point is walking from vertex of triangle to edge of triangle
            print('2->2')
            edgePair = meshWalkFromVertex()
            
            #if(np.linalg.det(d, edgePair[0]) == 0):
                #colinear
            #    colinearVal = 1
            #else:
            #    colinearVal = 0
                
            
        elif(pointLocationVar == 3):
            #point is walking from edge of triangle to edge of triangle
            print('3->2')
            triCoords = meshWalkFromEdge(triCoords[0], triCoords[1], triCoords[2], triCoordsSTU[0], triCoordsSTU[1], triCoordsSTU[2], dir) #assume direction vector d
            
            #testing array to store points:
            walkedPoints.append(np.array([currentPoint[0], currentPoint[1], 0.0], dtype=float))






    print('Coordinate array: ')
    for i, coords in enumerate(walkedPoints):
        print('coordinate number: ', i)
        print('coordinate value: ', coords[1], coords[0])
        world_x, world_y = rasterio.transform.xy(transf, coords[1], coords[0], offset='ul') #print in terms of world coords
        print('world coords:' , world_x.item(), world_y.item())


    print('-------------------------------------------------------------------------------------')
    print('start gpkg testing')

    print('bounds is: ', bounds)
    #readGPKG(gpkg_file_path)
