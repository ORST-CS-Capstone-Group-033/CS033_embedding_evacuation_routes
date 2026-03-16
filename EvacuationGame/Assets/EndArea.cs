using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EndArea : MonoBehaviour
{

    // having small stubby scripts is kinda bad design in my opinion, but since this does ONE thing
    // Start is called before the first frame update

    bool enteredBody = false;
    [SerializeField] GameSetup gameSetup;
    private void OnTriggerEnter(Collider collision)
    {
        Debug.Log(collision.gameObject.tag);
        if(collision.gameObject.tag == "Player" && enteredBody == false)
        {
            enteredBody = true;
            gameSetup.StartEndScript();
        }
    }
    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.tag == "Player" && enteredBody == false)
        {
            enteredBody = true;
            gameSetup.StartEndScript();
        }
    }
}
