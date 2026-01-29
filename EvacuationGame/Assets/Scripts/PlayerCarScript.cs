using UnityEngine;

public class PlayerCarScript : MonoBehaviour
{

    bool driving = true; // if false, the car cannot be controlled.
    bool lightsOn = false;
    [SerializeField] Rigidbody rb;
    [SerializeField] WheelCollider w1, w2, w3, w4;  // The four wheels,

    [SerializeField] float steeringSpeed;
    [SerializeField] float acceleration = 450f;
    private float currentAcceleration = 0f;
    float XInput, YInput;
    [SerializeField] float maxCarHealth;
    [SerializeField] float currentCarHealth;
    bool breaking = false;

    [SerializeField] GameObject CameraObject;
    [SerializeField] GameObject SteeringWheel;

    // Temporary, should be replaced with ball-joint swiveling camera
    Vector3 ogCamPos;
    Vector3 ogWheelPos;

    int cameraDirect = 0;
    float goalRotate = 45f;
    float minimumDamageForce = 100000f;

    // Start is called before the first frame update
    void Start()
    {
        ogCamPos = CameraObject.transform.localEulerAngles;
        ogWheelPos = SteeringWheel.transform.localEulerAngles;  
        driving = true;
        currentCarHealth = maxCarHealth;
    }

    // Update is called once per frame
    void Update()
    {
        DoCarInputs();
    }

    private void DoCarInputs()
    {

        XInput = Input.GetAxis("Horizontal");
        YInput = Input.GetAxis("Vertical");
        if (Input.GetKey(KeyCode.Space))
        {
            breaking = true;
        }
        else
        {
            breaking = false;
        }

        if (Input.GetKeyDown(KeyCode.L))
        {
            // put headlights here
            Debug.Log("Headlights");
            lightsOn = !lightsOn;
        }

        if (Input.GetKey(KeyCode.Q))
        {
            cameraDirect = 1;
        }
        else if (Input.GetKey(KeyCode.E))
        {
            cameraDirect = -1;
        }
        else
        {
            cameraDirect = 0;
        }
    }

    private void FixedUpdate() //  this is where physics are mostly applied.
    {

        if (!driving)
        {

            return;
        }
        //float engineCalcs = Input.GetAxis("Vertical") * drivingSpeed;
        currentAcceleration = Input.GetAxis("Vertical") * acceleration;
        w1.motorTorque = currentAcceleration;
        w2.motorTorque = currentAcceleration;
        w3.motorTorque = currentAcceleration;
        w4.motorTorque = currentAcceleration;
        w1.steerAngle = XInput * steeringSpeed;
        w2.steerAngle = XInput * steeringSpeed;
        if (breaking)
        {

            applyBrake();
        }
        else
        {
            w1.brakeTorque *= .25f;
            w2.brakeTorque *= .25f;

            if (w1.brakeTorque < 1f)
            {
                w1.brakeTorque = 0;
                w2.brakeTorque = 0;

            }
        }
        if (CameraObject)
        {

            Quaternion quatOfCamera = Quaternion.Euler(ogCamPos + new Vector3(0, (45f * -cameraDirect), 0));
            CameraObject.transform.localRotation = Quaternion.Lerp(CameraObject.transform.localRotation, quatOfCamera, .5f);

        }
        if (SteeringWheel)
        {

            Quaternion quatOfCamera = Quaternion.Euler(ogWheelPos + new Vector3((225f * -XInput), 0, 0));
            SteeringWheel.transform.localRotation = Quaternion.Lerp(SteeringWheel.transform.localRotation, quatOfCamera, steeringSpeed);
        }
    }
    /*
     * Applys damage to the car, currently non functional.
     */
    void applyCarDamage(float force)
    {
        currentCarHealth -= force;

        if(currentCarHealth < 0)
        {
            driving = false; // car has been destroyed
        }

    }

    private void OnCollisionEnter(Collision collision)
    {
        Vector3 collidePower = collision.impulse / Time.fixedDeltaTime;
        if (collidePower.magnitude > minimumDamageForce)
        {
            float dmg = collidePower.magnitude / 1000f;
            Mathf.Clamp(dmg, 100, 15000);

            applyCarDamage(dmg);
        }
    }
    void applyBrake() // brakes use the brakeTorque. most cars have brakes only in the front.
    {
        w1.brakeTorque = 3000f;
        w2.brakeTorque = 3000f;

    }
}
