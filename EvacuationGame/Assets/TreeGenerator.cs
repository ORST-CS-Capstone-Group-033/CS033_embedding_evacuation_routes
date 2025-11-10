using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using Unity.VisualScripting.Antlr3.Runtime.Tree;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UIElements;

public class TreeGenerator : MonoBehaviour
{
    // Start is called before the first frame update

    [SerializeField] Texture2D Treemap;
    [SerializeField] Texture2D Heightmappy;
    [SerializeField] List<GameObject> randomObjects;
    [SerializeField] GameObject treePrefab;

    int hardLimitTrees;
    [SerializeField] GameObject folder2PutTrees;
    [SerializeField] float treeProb = .99f;
    [SerializeField] MeshFilter meshfilty;
    int curTreeValue;
    int maxAmtVerts = 128;
    int skipBy = 4;
    int currentVerts = 0;
    void Start()
    {
        hardLimitTrees = 2048;

        DoTreeBullshit();
        
    }

    void DoTreeBullshit()
    {
        int step = 2; // only 2 for now

        int meshWidth = Heightmappy.width / step;
        int meshHeight = Heightmappy.height / step;

        Vector3[] verts = new Vector3[meshWidth * meshHeight];
        Vector2[] uv = new Vector2[verts.Length];
        int[] triangles = new int[(meshWidth - 1) * (meshHeight - 1) * 6];

    
        for (int y = 0; y < meshHeight; y++)
        {
            for (int x = 0; x < meshWidth; x++)
            {
        
                Color heightColor = Heightmappy.GetPixel(x * step, y * step);
                float heightValue = heightColor.grayscale * 10f;

                int i = y * meshWidth + x;
                verts[i] = new Vector3(x, heightValue, y);
                uv[i] = new Vector2((float)x / meshWidth, (float)y / meshHeight);

                Color pix = Treemap.GetPixel(x * step, y * step);

                if (pix.g > .5 && verts[i].y < 100)
                {

                    float randy = Random.value;

                    if (randy > treeProb && curTreeValue < hardLimitTrees)
                    {
                        curTreeValue++;

                        GameObject pickRandomForestObj = randomObjects[Random.Range(0,randomObjects.Count)];
                        GameObject gamer = Instantiate(pickRandomForestObj);
                        gamer.transform.parent = folder2PutTrees.transform;


                        gamer.transform.position =  new Vector3(verts[i].x * 16, verts[i].y * 16,verts[i].z * 16);
                        gamer.transform.localEulerAngles = new Vector3(gamer.transform.localEulerAngles.x,
                            gamer.transform.localEulerAngles.y + Random.Range(-180, 180),
                            gamer.transform.localEulerAngles.z);
                        // add variation later
                        //gamer.transform.Rotate()
                    }
                    else
                    {

                    }
                }
            }
        }

        // --- Generate triangles ---
        int t = 0;
        for (int y = 0; y < meshHeight - 1; y++)
        {
            for (int x = 0; x < meshWidth - 1; x++)
            {
                int i = y * meshWidth + x;

                // two triangles per quad
                triangles[t++] = i;
                triangles[t++] = i + meshWidth;
                triangles[t++] = i + 1;

                triangles[t++] = i + 1;
                triangles[t++] = i + meshWidth;
                triangles[t++] = i + meshWidth + 1;
            }
        }

        // --- Build mesh ---
        Mesh mesh = new Mesh();
        mesh.vertices = verts;
        mesh.triangles = triangles;
        mesh.uv = uv;
        mesh.RecalculateNormals();

        meshfilty.mesh = mesh; // Assign to your MeshFilter

        MeshCollider meshy =  gameObject.GetComponent<MeshCollider>();
        meshy.sharedMesh = null;
        meshy.sharedMesh = meshfilty.mesh;
    }

    /*
    if (pix.g > .5)
    {

        float randy = Random.value;

        if (randy > treeProb && curTreeValue < hardLimitTrees)
        {
            curTreeValue++;
            GameObject gamer = Instantiate(treePrefab);
            gamer.transform.parent = folder2PutTrees.transform;

            float avgVal = (nix.r + nix.g + nix.b) / 3;
            avgVal -= .5f;

            float xVal = i - Treemap.height / 2;
            float yVal = l - Treemap.width / 2;

            gamer.transform.position = new Vector3(xVal * 2,avgVal * 464,yVal * 2);
        }
        else
        {

        }
    }
    */


    // had to use chat to figure out mesh genning.



}
