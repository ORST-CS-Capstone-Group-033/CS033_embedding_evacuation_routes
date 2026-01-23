using UnityEngine;

public class RoadObstacleGenerator : MonoBehaviour
{
    [Header("Obstacle Settings")]
    public GameObject[] obstaclePrefabs;
    public int obstacleCount = 10;
    public float heightOffset = 0.5f;

    private Renderer roadRenderer;

    void Start()
    {
        roadRenderer = GetComponent<Renderer>();
        GenerateObstacles();
    }

    void GenerateObstacles()
    {
        Bounds bounds = roadRenderer.bounds;

        for (int i = 0; i < obstacleCount; i++)
        {
            float randomX = Random.Range(bounds.min.x, bounds.max.x);
            float randomZ = Random.Range(bounds.min.z, bounds.max.z);

            Vector3 spawnPos = new Vector3(
                randomX,
                bounds.max.y + heightOffset,
                randomZ
            );

            GameObject prefab = obstaclePrefabs[Random.Range(0, obstaclePrefabs.Length)];
            Instantiate(prefab, spawnPos, Quaternion.identity, transform);
        }
    }
}
