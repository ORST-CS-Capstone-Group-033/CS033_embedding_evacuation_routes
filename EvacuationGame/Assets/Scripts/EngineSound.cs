using System.Collections;
using UnityEngine;

public class EngineSound : MonoBehaviour
{
	public AudioSource idleSource;
	public AudioSource accelSource;

	[HideInInspector] public float sfxVolumeMultiplier = 1f;

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

		while (t < duration)
		{
			t += Time.unscaledDeltaTime;
			float lerp = 1f - (t / duration);

			idleSource.volume = Mathf.Lerp(0.25f, 0.05f, rb.velocity.magnitude / maxSpeed);
			accelSource.volume = Mathf.Lerp(0.0f, 0.7f, rb.velocity.magnitude / maxSpeed);

			yield return null;
		}
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
		idleSource.volume = Mathf.Lerp(0.25f, 0.05f, t) * sfxVolumeMultiplier;
		accelSource.volume = Mathf.Lerp(0.0f, 0.7f, t) * sfxVolumeMultiplier;
	}
}
