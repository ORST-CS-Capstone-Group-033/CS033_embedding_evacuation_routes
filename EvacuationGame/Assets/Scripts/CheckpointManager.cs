using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CheckpointManager : MonoBehaviour
{
    public static CheckpointManager Instance;

    [Header("Scoring Settings")]
    public int totalScore = 100;
    public int pointsLostPerSecond = 1;
    public int pointsLostWhenSkipped = 3;

    [Header("Checkpoint Settings")]
    public float checkpointRadius = 5f;
    public bool showCheckpoints = true;

    private float timer = 0f;
    private int currentCheckpointIndex = 0;

    private void Awake()
    {
        Instance = this;
    }

    private void Update()
    {
        timer += Time.deltaTime;
        totalScore -= Mathf.RoundToInt(pointsLostPerSecond * Time.deltaTime);
    }

    public void ReachCheckpoint(int index)
    {
        if (index == currentCheckpointIndex)
        {
            Debug.Log("Checkpoint Reached: " + index);
            currentCheckpointIndex++;
        }
        else if (index > currentCheckpointIndex)
        {
            Debug.Log("Checkpoint skipped! Penalty applied.");
            totalScore -= pointsLostWhenSkipped;
            currentCheckpointIndex = index + 1;
        }
    }
}
