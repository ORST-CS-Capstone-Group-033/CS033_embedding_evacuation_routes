using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class roadTestGeneration : MonoBehaviour
{
    [SerializeField] GameObject Roady;



    private void Start()
    {
        GenLoop();


    }

    void GenLoop()
    {
        Vector3 oldRoadyClonePos = transform.position;
        for (int i = 0; i < 100; i++)
        {

            GameObject roadyCLone = Instantiate(Roady);
            roadyCLone.transform.position = oldRoadyClonePos + new Vector3(Roady.transform.localScale.x - .01f, 0, 0);
            oldRoadyClonePos = roadyCLone.transform.position;
        }

    }
}