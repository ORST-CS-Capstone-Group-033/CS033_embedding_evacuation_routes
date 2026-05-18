using System.Collections.Generic;
using System.Data.Common;
using System.Drawing;
using System.Linq;
using UnityEngine;
using static UnityEditor.PlayerSettings;

public class PrototypeFoilageThing : MonoBehaviour
{
    // Start is called before the first frame update
    [SerializeField] float chunkSize = 64;
    Dictionary<Vector2Int, List<Vector3>> foliageGrid = new Dictionary<Vector2Int, List<Vector3>>();
    HashSet<Vector2Int> renderedChunks = new HashSet<Vector2Int>();
    Dictionary<Vector2Int, List<GameObject>> chunkObjects;
    [SerializeField] MeshFilter RoadMap;
    [SerializeField] List<GameObject> TreeObject = new List<GameObject>();
    [SerializeField] List<GameObject> Trees = new List<GameObject>();

    public GameObject plr;
    Vector2Int lastPoint;
    [SerializeField] LayerMask layers;
    Vector3 gridOrigin;
    int coinflip = 10;
    Vector2Int convert(Vector3 pos)
    {
        Vector3 lPos = pos - gridOrigin;
        return new Vector2Int(Mathf.FloorToInt(lPos.x / chunkSize), Mathf.FloorToInt(lPos.z / chunkSize));
    }
    void Start()
    {
        gridOrigin = RoadMap.transform.position;
        lastPoint = convert(plr.transform.position);

        chunkObjects = new Dictionary<Vector2Int, List<GameObject>>();
        for (int i = 0; i < 255; i++)
        {
            GameObject go = Instantiate(TreeObject[Random.Range(0,TreeObject.Count)]);
            go.transform.position = gameObject.transform.position;
            go.transform.Rotate(Vector3.up * Random.Range(-180, 180));
            go.SetActive(false);
            Trees.Add(go);
        }
        
        createTreeList();
        UpdateChunks(lastPoint);

    }
    Vector3 SnapPointToTerrain(Vector3 point)
    {
        Ray ray = new Ray(point + Vector3.up * 1000f, Vector3.down);  
        RaycastHit laser;
        if (Physics.Raycast(ray, out laser, 2000f, layers))
        {
            if (laser.collider.gameObject.layer != 6)
            {
                return laser.point;
            }
            else
            {
                Debug.Log("Failure to communicate..");
                return Vector3.zero;
            }
            //normals.Add(laser.n
            //}ormal);
        }
        else
        {
            Debug.Log("Failure to communicate..");
            return Vector3.zero;

        }
    }
    void createTreeList()
    {
        for (int i = -64; i < 64; i++)
        {

            for (int y = -64; y < 64; y++)
            {

                Vector2Int cell = new Vector2Int(i,y);
                List<Vector3> trees = new List<Vector3>();
                for (int s = 0; s < Random.Range(6,7); s++)
                {
                    Vector3 cellBasePos = gridOrigin + new Vector3(
                        cell.x * chunkSize,
                        0,
                        cell.y * chunkSize
                    );
                    Vector3 offset = cellBasePos + new Vector3(Random.Range(-chunkSize * .5f, chunkSize * .5f), 0, Random.Range(-chunkSize * .5f, chunkSize * .5f));


                    offset = SnapPointToTerrain(offset);
                    if(offset != Vector3.zero)
                    {
                        trees.Add(offset);
                    }
                }
                foliageGrid[cell] = trees;
                /*
                Vector3 Adjusted = new Vector3(RoadMap.transform.position.x + i * 2, 0, RoadMap.transform.position.z + y * 2);
                                    offset = SnapPointToTerrain(offset);

                if (foliageGrid.ContainsKey(convert(Adjusted)) == false)
                {
                    Ray ray = new Ray(newPoint + Vector3.up * 5f, Vector3.down);
                    RaycastHit laser;
                    if (Physics.Raycast(ray, out laser, 10f, layers))
                    {
                        if(laser.collider.gameObject.layer != 6)
                        {
                            foliageGrid.Add(convert(Adjusted), laser.point - new Vector3(0,-.5f,0));

                        }

                    }
                  

                }
                */

            }
        }
    }

    List<Vector3> MapToPointsonMesh(Vector3 pos)
    {
        Vector3 newpos = pos - new Vector3(-chunkSize,0,-chunkSize);
        List<Vector3> grandList = new List<Vector3>();
        for (int i = -0; i < 2; i++){

            for(int l = -0; l < 2; l++)
            {
                Vector2Int frick = convert(newpos + new Vector3((i * chunkSize) - chunkSize, 0, (l * chunkSize) - chunkSize));
                if (foliageGrid.ContainsKey(frick))
                {
                    grandList.AddRange(foliageGrid[frick]);

                }
            }
           

        }
        if(grandList.Count > 0)
        {
            return grandList;

        }
        return null;

    }
    void UpdateChunks(Vector2Int currentCell)
    {
        HashSet<Vector2Int> desired = new HashSet<Vector2Int>();

        for (int x = -2; x <= 3; x++)
        {
            for (int y = -2; y <= 3; y++)
            {

                desired.Add(currentCell + new Vector2Int(x, y));
            }
        }

        List<Vector2Int> toRemove = new List<Vector2Int>();

        foreach (var kvp in chunkObjects)
        {
            if (!desired.Contains(kvp.Key))
            {
                foreach (var obj in kvp.Value)
                    obj.SetActive(false);

                toRemove.Add(kvp.Key);
            }
        }

        foreach (var c in toRemove)
            chunkObjects.Remove(c);
        int total = 0;

        foreach (var c in desired)
        {
            if (chunkObjects.ContainsKey(c) || !foliageGrid.ContainsKey(c))
            {
                continue;

            }
            List<GameObject> objs = new List<GameObject>();
            foreach (Vector3 pos in foliageGrid[c])
            {

                total++;
                GameObject free = Trees.FirstOrDefault(t => !t.activeSelf);
                if (!free) break;

                free.transform.position = pos;
                free.transform.rotation = Quaternion.Euler(0, Random.Range(-180, 180), 0);
                free.SetActive(true);

                objs.Add(free);
            }
            chunkObjects[c] = objs;
        }
        Debug.Log("Tress Rendered: " + total);

    }

    // Update is called once per frame
    void FixedUpdate()
    {
        if (coinflip % 5 == 0)
        {
            Vector2Int currentCell = convert(plr.transform.position);
           
            if (currentCell != lastPoint)
            {
                lastPoint = currentCell;


                UpdateChunks(currentCell);

                /*
                if (result == null)
                {
                    return;
                }
                int totalTreeList = Mathf.Min(Trees.Count, result.Count);

                for (int i = 0; i < totalTreeList; i++){

                    if (Mathf.Abs(Vector3.Distance(result[i], plr.transform.position)) > 5)
                    {
                        Trees[i].transform.position = result[i];
                        Trees[i].SetActive(true);

                    }
                  


                }
                */
              
            }
               
            //MapToPointsonMesh(plr.transform.position);
            coinflip++;

        }
        else
        {
            coinflip++;
        }
    }
}
