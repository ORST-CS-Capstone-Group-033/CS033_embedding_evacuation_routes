using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

public class WheelVisuals : MonoBehaviour
{

    // this has no effect on physics, but is vital for wheel visuals.
    bool canWheel = true;
    [SerializeField] WheelCollider wheelParent;
    public Transform wheel;

    Vector3 pos;
    Quaternion rot;
    private void Start()
    {
    }
    void Update() // the wheels tend to glitch from time to tim
    {
        wheel.Rotate(0, -wheelParent.rpm / 60 * 360 * Time.deltaTime, 0);

        if (canWheel) // if the wheel is active, spin it
        {
            wheel.localEulerAngles = new Vector3(wheel.localEulerAngles.x, 90 + wheelParent.steerAngle - wheel.localEulerAngles.z, wheel.localEulerAngles.z);

        }
        wheelParent.GetWorldPose(out pos, out rot);
        wheel.transform.position = pos;

    }
}
