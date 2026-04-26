using System.Collections;
using UnityEngine;

public class EngineSound : MonoBehaviour
{
	public AudioSource idleSource;
	public AudioSource accelSource;

	public float maxSpeed = 20f;
	public float minPitch = 0.8f;
	public float maxPitch = 2.0f;

	private Rigidbody rb;

	void Start()
	{
		rb = GetComponent<Rigidbody>();
	}

	public void FadeOutEngine(float duration)
	{
		StartCoroutine(FadeOutRoutine(duration));
	}

	private IEnumerator FadeOutRoutine(float duration)
	{
		float t = 0f;
		float startIdle = idleSource.volume;
		float startAccel = accelSource.volume;

		while (t < duration)
		{
			t += Time.unscaledDeltaTime;
			float lerp = 1f - (t / duration);
			idleSource.volume = startIdle * lerp;
			accelSource.volume = startAccel * lerp;

			yield return null;
		}

		idleSource.volume = 0f;
		accelSource.volume = 0f;
	}

	private void Update()
	{
		float speed = rb.velocity.magnitude;
		float t = Mathf.Clamp01(speed / maxSpeed);

		// Pitch shift both sounds
		float pitch = Mathf.Lerp(minPitch, maxPitch, t);
		idleSource.pitch = pitch;
		accelSource.pitch = pitch;

		// Blend volumes
		idleSource.volume = Mathf.Lerp(0.25f, 0.05f, t);
		accelSource.volume = Mathf.Lerp(0.0f, 0.7f, t);
	}
}
