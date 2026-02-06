using UnityEngine;
using System.Collections.Generic;

public class RoadObstacleGenerator : MonoBehaviour
{
    [Header("Obstacle Settings")]
    public GameObject[] obstaclePrefabs;
    public int obstacleCount = 10;
    public float heightOffset = 0.5f;

    [Header("Spacing Settings")]
    public float minXSpacing = 3f;       // Side-to-side clearance
    public int maxSpawnAttempts = 20;

    private Renderer roadRenderer;

    void Start()
    {
        roadRenderer = GetComponent<Renderer>();
        GenerateObstacles();
    }

    void GenerateObstacles()
    {
        Bounds bounds = roadRenderer.bounds;
        List<Vector3> usedPositions = new List<Vector3>();

        int spawned = 0;
        int attempts = 0;

        while (spawned < obstacleCount && attempts < obstacleCount * maxSpawnAttempts)
        {
            attempts++;

            float randomX = Random.Range(bounds.min.x, bounds.max.x);
            float randomZ = Random.Range(bounds.min.z, bounds.max.z);

            Vector3 spawnPos = new Vector3(
                randomX,
                bounds.max.y + heightOffset,
                randomZ
            );

            bool tooClose = false;

            // ✅ Check horizontal (X) spacing only
            foreach (Vector3 pos in usedPositions)
            {
                if (Mathf.Abs(spawnPos.x - pos.x) < minXSpacing)
                {
                    tooClose = true;
                    break;
                }
            }

            if (tooClose)
                continue;

            GameObject prefab = obstaclePrefabs[Random.Range(0, obstaclePrefabs.Length)];

            // Instantiate in world space, then parent safely
            GameObject obstacle = Instantiate(prefab, spawnPos, Quaternion.identity);
            obstacle.transform.SetParent(transform, true);

            usedPositions.Add(spawnPos);
            spawned++;
        }
    }
}
