using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameSetup : MonoBehaviour
{
    // Start is called before the first frame update

    [SerializeField] GameObject RoadObject;
    float obstacleLikelyhood = .25f;
    [SerializeField] List<GameObject> roadObjects = new List<GameObject>();
    [SerializeField] GameObject objectContainer;

    int Score = 10000;
    int MaxScore = 10000;
    bool gameRunning = false;
    public PrototypeTerrainThing obstacleGenerator; 
    [SerializeField] TextMeshProUGUI ScoreEndText;

	// reference to the final time text     -- MM
    [SerializeField] TextMeshProUGUI finalTimeText;

    // reference to the final UI panel      -- MM
    [SerializeField] GameObject finalPanel;

    // reference to the timer UI script     -- MM
    [SerializeField] TimerUI timerUI;

    // reference to the fact panel          -- MM
    [SerializeField] FactPanel factPanel;

    PlayerCarScript pCar;

    void Start()
    {
        if (RoadObject)
        {
            //roadSetup();
        }

        gameRunning = true;

		// get the fact panel instance      -- MM
        factPanel = FactPanel.Instance;

        // get the player car script        -- MM
        pCar = FindObjectOfType<PlayerCarScript>();
        if (obstacleGenerator)
        {
            obstacleGenerator.CreateObstacles(Vector3.zero);
        }

    }

	Vector3 readNextPoint(JsonPoint pointy) // this inherently does mapping to the origin point
    {
        Vector3 goobah = RoadObject.transform.position + new Vector3(
            -pointy.x * RoadObject.transform.localScale.x / 100,
            pointy.z * RoadObject.transform.localScale.y / 100,
            pointy.y * RoadObject.transform.localScale.z / 200);

        return goobah;
    }

    void SpawnPile(Vector3 p1, Vector3 p2)
    {
        for (int i = 0; i < Random.Range(5, 10); i++)
        {
            Vector3 midPoint = (p1 + p2) * .5f;

            // Finally, we add some flux.

            Vector3 finalResult = midPoint + new Vector3(Random.Range(-10.5f, 10.5f), 0, Random.Range(-10.5f, 10.5f));
            GameObject obstacleClone = Instantiate(roadObjects[Random.Range(0, roadObjects.Count)]);
            obstacleClone.transform.position = finalResult;
            obstacleClone.transform.rotation = Quaternion.LookRotation((p1 - p2).normalized);

        }

    }

   

    // Updated for no coroutine, no auto-reload     -- MM
    public void StartEndScript()
    {
        if (!gameRunning)
            return;

        gameRunning = false;

        // Stop the car                     -- MM
        pCar.driving = false;

        // Pause the game                   -- MM
        Time.timeScale = 0f;

		// Show the final score             -- MM
        ScoreEndText.text = "Total Danger Left: " + Score.ToString();
        ScoreEndText.enabled = true;

        // Show final time                  -- MM
        finalTimeText.text = "Time: " + timerUI.GetFinalTime().ToString("0.00");

		// Show the final UI panel          -- MM
        finalPanel.SetActive(true);

        // Show the fact panel              -- MM
        
        var (theme, source, quote) = FactManager.Instance.GetRandomFact();
        factPanel.Show(theme, source, quote);
	}

/* Logic added to StartEndScript()          -- MM
	IEnumerator EndScript()
    {
        gameRunning = false;

        ScoreEndText.text = "Total Danger Left: " + Score.ToString();
        ScoreEndText.enabled = true;
        pCar.driving = false;
        yield return new WaitForSeconds(5f);
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    } */

    public void ModScore(int amount)
    {
        Score -= amount;

    }

	// Reset level button logic             -- MM
    public void RestartLevel() {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }
}