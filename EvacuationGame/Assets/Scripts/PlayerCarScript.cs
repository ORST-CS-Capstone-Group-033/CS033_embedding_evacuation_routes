using UnityEngine;

public class PlayerCarScript : MonoBehaviour
{

    bool driving = true; // if false, the car cannot be controlled.
    bool lightsOn = false;
    public Rigidbody rb;
    public WheelCollider w1, w2, w3, w4;  // The four wheels,

    [SerializeField] float steeringSpeed;
    [SerializeField] float acceleration = 450f;
    private float currentAcceleration = 0f;
    float XInput, YInput;
    [SerializeField] float maxCarHealth;
    private float currentCarHealth;
    bool breaking = false;
    // Start is called before the first frame update
    void Start()
    {
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
    }

    private void FixedUpdate() //  this is where physics are mostly applied.
    {
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
    }
    /*
     * Applys damage to the car, currently non functional.
     */
    void applyCarDamage(float force)
    {

        currentCarHealth -= Mathf.Clamp(force * 1.5f,0,1000); // this will need to be tacked to something more substantial
        if (currentCarHealth < 0)
        {
            driving = false;
        }
        else
        {

            // space for damage visuals
        }
    }
    void applyBrake() // brakes use the brakeTorque. most cars have brakes only in the front.
    {
        w1.brakeTorque = 3000f;
        w2.brakeTorque = 3000f;

    }
}
