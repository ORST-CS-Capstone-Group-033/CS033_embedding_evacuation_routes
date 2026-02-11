using System;
using System.Collections.Generic;
using UnityEngine;

public class PlayerCarScript : MonoBehaviour
{

    bool driving = true; // if false, the car cannot be controlled.
    bool lightsOn = false;
    bool breaking = false;


    [SerializeField] Rigidbody rb; 
    [SerializeField] WheelObject w1, w2, w3, w4;

    [SerializeField] List<Light> Headlights = new List<Light>(); // again, not notable enough to be its own thing
    [SerializeField] float steeringSpeed;
    [SerializeField] float acceleration = 450f;
    private float currentAcceleration = 0f;
    float XInput, YInput;
    [SerializeField] float maxCarHealth;
    [SerializeField] float currentCarHealth;
    [SerializeField] GameObject Speedometer; // the dial that signals our speed
    [SerializeField] GameObject CameraObject;
    [SerializeField] GameObject SteeringWheel;
    [SerializeField] float maxEngineTorque = 1000f; // The maximum RPM the wheels are allowed to spin. 
    // In reality, cars would start to suffer from overrev damage.
    // Temporary, should be replaced with ball-joint swiveling camera

    Vector3 ogCamPos;
    Vector3 ogWheelPos;

    int cameraDirect = 0;
    float goalRotate = 45f;
    float minimumDamageForce = 100000f; // the minimum amount of newtons needed to do actual damage to the car.
    private float recAngularVelo = 0f;

    [SerializeField] GameObject CrashEffect; // gameobject that is genreated during a crash.
    // Start is called before the first frame update
    void Start()
    {
        rb.centerOfMass += new Vector3(0, -.75f, 0);

        ogCamPos = CameraObject.transform.localEulerAngles;
        ogWheelPos = SteeringWheel.transform.localEulerAngles;
        driving = true;
        currentCarHealth = maxCarHealth;
    }

    // Update is called once per frame
    void Update()
    {
        DoCarInputs();

        if (Speedometer)
        {

            SpeedoTest();
        }
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

        if (Input.GetKeyDown(KeyCode.R))
        {

            ToggleHeadlights();
        }
    }
    private void ToggleHeadlights() // very simple organized function that just toggles lights on and off
    {

        for(int i = 0; i < Headlights.Count; i++)
        {

            Headlights[i].enabled = !Headlights[i].enabled;
        }
    }
    private void SpeedoTest()
    {

        float divisive = recAngularVelo / maxEngineTorque; // record whatever acceleration we have and factor it against our max engine torque
        Speedometer.transform.localRotation = Quaternion.Euler(0,divisive * 270f,0);
        //Speedometer.transform.Rotate(Speedometer.transform.up, .25f * Time.fixedDeltaTime); // obselete but still good
    }
    private void FixedUpdate() //  this is where physics are mostly applied.
    {
        //rb.AddForce(-Vector2.up * 10000f);


        if (rb.velocity.y <= 1 - 0)
        {



        }
        if (!driving)
        {

            return;
        }
        //float engineCalcs = Input.GetAxis("Vertical") * drivingSpeed;
        currentAcceleration = Input.GetAxis("Vertical") * acceleration;

        DoWheelMath(w1, true); // front left, front right, bottom left, bottom right
        DoWheelMath(w2, true);
        DoWheelMath(w3, false);
        DoWheelMath(w4, false);
       
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
    void applyCarDamage(float force, Vector3 hitPos)
    {
        currentCarHealth -= force;
       
        if (CrashEffect && force > 350f) // if its a big hit, show it accordingly with sparks
        {
            GameObject crashEffectClone = Instantiate(CrashEffect, transform.parent);

            crashEffectClone.transform.position = hitPos;
            crashEffectClone.GetComponent<ParticleSystem>().Emit(UnityEngine.Random.Range(5,10)); // a crash effect must have particle system inside.
            Destroy(crashEffectClone, 1.5f);
        }
        if (currentCarHealth < 0)
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

            applyCarDamage(dmg, collision.GetContact(0).point);
        }
    }
    private float computeWheelForce(WheelObject w, float forward, float doubleSpring) 
    {

        // wheel surface speed at contact patch
        float wheelSurfaceSpeed = w.angularVelocity * w.wheelRadius; // the current speed of our wheel.

        float slip = (wheelSurfaceSpeed - forward) / Mathf.Max(Mathf.Abs(forward), 1f); // whichever is higher...
        // determine the slip ratio

        float tireForce = slip * w.frontGripLevel * doubleSpring * 1.2f;

        return Mathf.Clamp(tireForce, -doubleSpring, doubleSpring);


    }

    private void DoWheelMath(WheelObject w, bool steering = false)
    {
        Vector3 wOrigin = w.WheelTF.position;
        float rayAmount = w.wheelRadius + w.suspensionRest;

        bool b = Physics.Raycast(wOrigin, -transform.up, out RaycastHit hit, rayAmount);

        if (b)
        {
            w.grounded = true;

            float currentOffset = w.suspensionRest - (hit.distance - w.wheelRadius); // how compressed are we?


            currentOffset = Math.Clamp(currentOffset, 0, w.suspensionRest);
            // now get the force
            float springForce = currentOffset * w.springStrength;
            // dampen it
            float dampeningLevel = (currentOffset - w.compression) / Time.fixedDeltaTime; // idk

            float damperPower = dampeningLevel * w.springDampening;
            damperPower = Math.Clamp(damperPower, -springForce, springForce);

            w.compression = currentOffset; // update the compression based on our calculations, and then add a according force.

            // now add this to the force...
            rb.AddForceAtPosition(transform.up * (springForce + damperPower), hit.point);
            Vector3 wheelContactPointVelo = rb.GetPointVelocity(hit.point); // velocity at hit point

            Vector3 forward;

            if (steering)
            {
                // Vibecoded part that gets the vector we want to apply forward force in.
                forward = Quaternion.AngleAxis(XInput * steeringSpeed, hit.normal) * transform.forward;
                steeringVisuals(w);

            }
            else
            {
                forward = transform.forward;
            }


            // lateral(sliding force) is the hardest part of this.
            forward = Vector3.ProjectOnPlane(forward, hit.normal).normalized;
            Vector3 rightward = Vector3.Cross(hit.normal, forward).normalized;


            float forwardSpeed = Vector3.Dot(wheelContactPointVelo, forward); // how much it wants to go forward
            float rightWardSpeed = Vector3.Dot(wheelContactPointVelo, rightward); // how much it wishes to go rightward
            float desiredVSwanted = Mathf.Atan2(rightWardSpeed, Mathf.Abs(forwardSpeed) + .05f); // add slight bias, this is essentially how much it wishes o go.s
            float desiredAcceleration = currentAcceleration;



            float computedWheelForce = computeWheelForce(w, forwardSpeed, (springForce + damperPower));
            if (YInput == -1 && w.angularVelocity < 0.1f) desiredAcceleration *= .25f;

           // a car's reverse gear usually has significantly less power
            // 1.5f is inertia, the higher it is the more the wheels resist against being changed in speed
            w.angularVelocity += (((-computedWheelForce * w.wheelRadius) + desiredAcceleration) / 1.5f) * Time.fixedDeltaTime; // doohickey equation


            rb.AddForceAtPosition((forward * computedWheelForce), hit.point); // forward acceleration, note the dumb way we apply grip.
                                                                              // now add drag



            /// Rightward force is the velocity, times griplevel(the amonunt we will tolerate, 
            float resultingSlipProduct = (-desiredVSwanted * w.sideGripLevel) * (springForce + damperPower);

            resultingSlipProduct = Mathf.Clamp(resultingSlipProduct, (springForce + damperPower) * -50f, (springForce + damperPower) * 50f); // why are we clamping?
            rb.AddForceAtPosition(rightward * resultingSlipProduct, hit.point);

           
            if (breaking && steering)
            {
                rb.AddForceAtPosition(-forward * (550f * forwardSpeed * w.frontGripLevel), hit.point);
            }
        }
        else
        {
            w.grounded = false;
        }
        w.WheelTF.Rotate(-Vector3.up, Time.fixedDeltaTime * (w.angularVelocity * w.wheelRadius) * Mathf.Rad2Deg, Space.Self); //deltatime is calaced earlier on.

        w.angularVelocity = Mathf.Clamp(w.angularVelocity, -maxEngineTorque, maxEngineTorque); // be sure to clamp velocity.

        w.angularVelocity *= .975f;

        if(w == w3) // only one non-steering wheel records 
        {
            recAngularVelo = Mathf.Abs(w.angularVelocity); // steering wheels control
        }
    }

    void steeringVisuals(WheelObject w)
    {
        float steerangles = XInput * 35f;

        w.WheelTF.parent.localRotation = Quaternion.Euler(0f, steerangles, 0f);

      

    }

}
