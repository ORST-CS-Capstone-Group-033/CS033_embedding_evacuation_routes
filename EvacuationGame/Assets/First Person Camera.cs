using UnityEngine;
using UnityEngine.InputSystem; // <-- new input system

public class FirstPersonCamera : MonoBehaviour
{
    public Transform player;
    public float mouseSensitivity = 2f;

    float cameraVerticalRotation = 0f;
    bool lockedCursor = true;
    Vector2 lookInput;

    void Start()
    {
        // Lock and hide cursor
        Cursor.visible = false;
        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        // Read mouse delta from new Input System
        if (Mouse.current != null)
        {
            lookInput = Mouse.current.delta.ReadValue();
        }

        float inputX = lookInput.x * mouseSensitivity * Time.deltaTime * 100f;
        float inputY = lookInput.y * mouseSensitivity * Time.deltaTime * 100f;

        // Vertical rotation (camera)
        cameraVerticalRotation -= inputY;
        cameraVerticalRotation = Mathf.Clamp(cameraVerticalRotation, -90f, 90f);
        transform.localEulerAngles = Vector3.right * cameraVerticalRotation;

        // Horizontal rotation (player)
        player.Rotate(Vector3.up * inputX);
    }
}
