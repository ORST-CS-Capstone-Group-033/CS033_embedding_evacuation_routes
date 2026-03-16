using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class EdgeMarker
{
    public JSONPoints[] edges;
}
[System.Serializable]
public class JSONPoints
{
    public JsonPoint p1;
    public JsonPoint p2;
}
[System.Serializable]
public class JsonPoint
{
    public float x; public float y; public float z;
}