using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FactManager : MonoBehaviour {
	public static FactManager Instance { get; private set; }

	public FactsRoot facts;

	void Awake()
	{
		if (Instance != null && Instance != this)
		{
			Destroy(gameObject);
			return;
		}
		Instance = this;
		DontDestroyOnLoad(gameObject);

		LoadFacts();
	}

	void LoadFacts()
	{
		TextAsset json = Resources.Load<TextAsset>("facts");
		if (json == null)
		{
			Debug.LogError("facts.json not found in Resources!");
			return;
		}

		facts = JsonUtility.FromJson<FactsRoot>(json.text);
	}

	public (string theme, string source, string quote) GetRandomFact() {
		// Collect themes
		var themes = new List<(string key, ThemeFacts tf)>();

		if (facts.landslide_science != null) themes.Add(("landslide_science", facts.landslide_science));
		if (facts.evacuation_behavior != null) themes.Add(("evacuation_behavior", facts.evacuation_behavior));
		if (facts.post_disaster_safety != null) themes.Add(("post_disaster_safety", facts.post_disaster_safety));
		if (facts.risk_awareness != null) themes.Add(("risk_awareness", facts.risk_awareness));

		if (themes.Count == 0) return ("", "", "");

		var themeIdx = UnityEngine.Random.Range(0, themes.Count);
		var (themeKey, themeFacts) = themes[themeIdx];

		if (themeFacts.sources == null || themeFacts.sources.Count == 0)
			return (themeKey, "", "");

		var sourceIdx = UnityEngine.Random.Range(0, themeFacts.sources.Count);
		var sourceBlock = themeFacts.sources[sourceIdx];

		if (sourceBlock.quotes == null || sourceBlock.quotes.Count == 0)
			return (themeKey, sourceBlock.source, "");

		var quoteIdx = UnityEngine.Random.Range(0, sourceBlock.quotes.Count);
		var quote = sourceBlock.quotes[quoteIdx];

		return (themeKey, sourceBlock.source, quote);
	}
}