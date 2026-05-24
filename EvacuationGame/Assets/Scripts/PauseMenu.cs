using UnityEngine;
using UnityEngine.SceneManagement;

public class PauseMenu : MonoBehaviour
{
	public GameObject pausePanel;
	public GameSetup gameSetup;
	public EngineSound engineSound;

	public AudioSource musicSource;
	public AudioSource[] sfxSources;

	public UnityEngine.UI.Slider musicSlider;
	public UnityEngine.UI.Slider sfxSlider;
	public UnityEngine.UI.Slider masterSlider;

	float originalMusicVolume;
	float[] originalSFXVolumes;

	float musicVolumeScale = 0.5f;
	float sfxVolumeScale = 0.5f;
	float masterVolume = 1f;

	bool isPaused = false;

	void Start()
	{
		if (musicSource != null)
			originalMusicVolume = musicSource.volume;

		originalSFXVolumes = new float[sfxSources.Length];
		for (int i = 0; i < sfxSources.Length; i++)
			originalSFXVolumes[i] = sfxSources[i].volume;

		if (musicSlider != null)
			musicSlider.value = musicVolumeScale;

		if (sfxSlider != null)
			sfxSlider.value = sfxVolumeScale;

		if (masterSlider != null)
			masterSlider.value = masterVolume;

		ApplyVolumes();
	}

	private void Update()
	{
		if (!gameSetup.gameEnded && Input.GetKeyDown(KeyCode.Escape))
		{
			if (isPaused) ResumeGame();
			else PauseGame();
		}
	}

	public void PauseGame()
	{
		isPaused = true;
		pausePanel.SetActive(true);
		Time.timeScale = 0f;

		if (musicSource != null)
			musicSource.Pause();

		foreach (var s in sfxSources)
			s.Pause();
	}

	public void ResumeGame()
	{
		isPaused = false;
		pausePanel.SetActive(false);
		Time.timeScale = 1f;

		if (musicSource != null)
			musicSource.UnPause();

		foreach (var s in sfxSources)
			s.UnPause();
	}

	public void RestartGame()
	{
		Time.timeScale = 1f;
		SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
	}

	public void ExitGame()
	{
		Application.Quit();
	}

	public void SetMusicVolume(float v)
	{
		musicVolumeScale = v;
		ApplyVolumes();
	}

	public void SetSFXVolume(float v)
	{
		sfxVolumeScale = v;
		ApplyVolumes();
	}

	public void SetMasterVolume(float v)
	{
		masterVolume = v;
		ApplyVolumes();
	}

	void ApplyVolumes()
	{
		if (musicSource != null)
			musicSource.volume = originalMusicVolume * musicVolumeScale * masterVolume;
		for (int i = 0; i < sfxSources.Length; i++)
			sfxSources[i].volume = originalSFXVolumes[i] * sfxVolumeScale * masterVolume;
		engineSound.sfxVolumeMultiplier = sfxVolumeScale * masterVolume;
		Debug.Log("SFX volume applie: " + sfxSources[0].volume);
	}
}
