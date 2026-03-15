using TMPro;
using UnityEngine;

public class TimerUI : MonoBehaviour
{
	public TMP_Text timerText;
	float elapsed;

	void Update()
	{
		elapsed += Time.deltaTime;
		timerText.text = elapsed.ToString("0.00");
	}

	public float GetFinalTime() => elapsed;
}
