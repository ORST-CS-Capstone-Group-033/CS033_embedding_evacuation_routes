using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[System.Serializable]
public class WheelObject
{
    // Start is called before the first frame update
    public float wheelRadius;
    public Transform WheelTF;
    public float suspensionRest = .2f;
    public float maxSuspension = .5f; // what it can extend to

    public float springStrength = 35000f;
    public float springDampening = 3000f;

    public float frontGripLevel, sideGripLevel = .5f;

    [HideInInspector] public float compression; // how compressed are we 
    [HideInInspector] public bool grounded; // if we are grounded or not
    [HideInInspector] public float angularVelocity; // whats the angular velocity?
}
