using System;
using System.Collections;
using System.Collections.Generic;

[Serializable]
public class SourceQuotes {
	public string source;
	public List<string> quotes;
}

[Serializable]
public class ThemeFacts {
	public List<SourceQuotes> sources;
}

[Serializable]
public class FactsRoot {
	public ThemeFacts landslide_science;
	public ThemeFacts evacuation_behavior;
	public ThemeFacts post_disaster_safety;
	public ThemeFacts risk_awareness;
}