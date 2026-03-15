using UnityEngine;
using TMPro;

public class FactPanel : MonoBehaviour {
	public static FactPanel Instance;

	[Header("UI References")]
	public CanvasGroup canvasGroup;
	public TMP_Text themeText;
	public TMP_Text quoteText;
	public TMP_Text sourceText;

	void Awake() {
		Instance = this;
		HideImmediate();
	}

	public void Show(string theme, string source, string quote) {
		themeText.text = ThemeToDisplayName(theme);
		quoteText.text = quote;
		sourceText.text = "- " + FormatSourceName(source);

		canvasGroup.alpha = 1f;
		canvasGroup.interactable = true;
		canvasGroup.blocksRaycasts = true;
	}

	public void HideImmediate() {
		canvasGroup.alpha = 0f;
		canvasGroup.interactable = false;
		canvasGroup.blocksRaycasts = false;
	}

	string ThemeToDisplayName(string key) {
		return key switch {
			"landslide_science" => "Landslide Science",
			"evacuation_behavior" => "Evacuation Behavior",
			"post_disaster_safety" => "Post-Disaster Safety",
			"risk_awareness" => "Risk Awareness",
			_ => key
		};
	}

	string FormatSourceName(string raw) {
		return raw switch
		{
			"ready_gov" => "Ready.gov",
			"cdc" => "CDC",
			"usgs" => "USGS",
			"crs" => "CRS",
			_ => raw
		};
	}

#if UNITY_EDITOR
	[ContextMenu("Test Show Fact Panel")]
	void TestShowRandom() {
		var (theme, source, quote) = FactManager.Instance.GetRandomFact();
		Show(theme, source, quote);
	}
#endif
}