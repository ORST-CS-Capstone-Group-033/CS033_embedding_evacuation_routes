using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Checkpoint : MonoBehaviour
{
    public int index;
    public bool isActive = false;

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            CheckpointManager.Instance.ReachCheckpoint(index);
            isActive = true;
        }
    }

    // Debug visibility toggle
    private void OnDrawGizmos()
    {
        if (CheckpointManager.Instance != null && CheckpointManager.Instance.showCheckpoints)
        {
            Gizmos.color = isActive ? Color.green : Color.red;
            Gizmos.DrawWireSphere(transform.position, CheckpointManager.Instance.checkpointRadius);
        }
    }
}
