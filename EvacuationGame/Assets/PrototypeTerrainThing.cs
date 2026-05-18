using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class PrototypeTerrainThing : MonoBehaviour
{
  
    // Start is called before the first frame update

    [SerializeField] MeshFilter RoadMap;
    [SerializeField] float roadScale = 10f;
    [SerializeField] List<GameObject> RoadObjects = new List<GameObject>();
    List<GameObject> obstacles = new List<GameObject>();
    List<Vector3> normals = new List<Vector3>();
    [SerializeField] GameObject Terrain;
    [SerializeField] GameObject folder;
    [SerializeField] LayerMask layers;
    [System.Serializable]
    public class PointContainer
    {

        public PointPoint[] pointContainer;// fuck it i dont give a fucking damn about this its 2 am
    }
    [System.Serializable]
    public class PointPoint
    {
        public float x, y, z;

    }

    Vector3 SnapPointToTerrain(Vector3 point, Vector3 adjustor)
    {
        Ray ray = new Ray(RoadMap.gameObject.transform.position + point + (Vector3.up * 200f) + adjustor, Vector3.down);
        RaycastHit laser;
        if (Physics.Raycast(ray, out laser, 2000f, layers))
        {
            return laser.point;
            //normals.Add(laser.normal);
        }
        else
        {
            Debug.Log("Failure to communicate..");
            return point;

        }
    }
    Vector3 ScaleUP(PointPoint point)
    {
        return new Vector3(point.x * roadScale, point.z * roadScale, point.y * roadScale);
    }
    public void CreateObstacles(Vector3 adjustorA)
    {
        TextAsset bezierJSON = Resources.Load<TextAsset>("RoadAdvanced");
        PointContainer data = JsonUtility.FromJson<PointContainer>(bezierJSON.text);
        Debug.Log(data);
        for (int i = 0; i < data.pointContainer.Length; i++)
        {
            if (i < data.pointContainer.Count() - 3 && i % 3 == 0)
            {
                int rando = Random.Range(0, 100);
                if (rando < 5){
                    // spaghetti but ehh
                    Debug.Log("Doit");
                    GameObject goobah = Instantiate(RoadObjects[Random.Range(0, RoadObjects.Count)], folder.transform);
                    Vector3 pointA = ScaleUP(data.pointContainer[i]);
                    Vector3 pointB = ScaleUP(data.pointContainer[i + 3]);
                    pointA = SnapPointToTerrain(pointA, adjustorA);
                    pointB = SnapPointToTerrain(pointB, adjustorA);
                    Vector3 directionC = (pointB - pointA);
                    float length = directionC.magnitude;
                    Vector3 normal = directionC.normalized;

                    if (length < .01 || length > 100f)
                    {
                        continue;
                    }
                    goobah.transform.position = pointA + normal * (length * .5f);
                    goobah.transform.position += goobah.transform.up * .5f;

                    Vector3 normalizedpointA = NormalizePoint(pointA);
                    Vector3 normalizedpointB = NormalizePoint(pointB);
                    Vector3 midPoint = (normalizedpointA + normalizedpointB).normalized;
                    goobah.transform.rotation = Quaternion.LookRotation(directionC.normalized, midPoint);
                    goobah.transform.Rotate(goobah.transform.up * Random.Range(-90, 90));
                    obstacles.Add(goobah);
                }
               
            }



        }

    }
    Vector3 NormalizePoint(Vector3 point)
    {
        Ray ray = new Ray(point + Vector3.up * 200f, Vector3.down);
        RaycastHit hit;

        if (Physics.Raycast(ray, out hit, 2000f, layers))
        {
            return hit.normal;
        }

        return Vector3.up;
    }

    // artifacted...
    void AdjustRoads()
    {

        for (int i = 0; i < obstacles.Count - 1; i++)
        {
            Ray ray = new Ray(obstacles[i].transform.position + Vector3.up * 200f, Vector3.down);
            RaycastHit laser;
            if (Physics.Raycast(ray, out laser, 2000f, layers))
            {
                obstacles[i].transform.position = laser.point + new Vector3(0, .1f, 0);
                normals.Add(laser.normal);
            }
            else
            {
                normals.Add(Vector3.up);

            }

        }
        for (int i = 0; i < obstacles.Count - 1; i++)
        {

            Vector3 forward = (obstacles[i + 1].transform.position - obstacles[i].transform.position).normalized;

            obstacles[i].transform.rotation = Quaternion.LookRotation(forward, normals[i]) * Quaternion.Euler(0, 0, 90);


        }
    }
}
