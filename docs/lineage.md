# MLCA lineage

This is new code, not a port of LlamaIndex. Historical events map to the following workflow concepts:
InitializeEvent → onboard; ListFilesEvent/LoadDataEvent → data inventory;
PreprocessEvent → split then preprocess; TrainEvent → model;
EvaluateEvent → validate and deliberately unlocked test;
PlotEvent → event-specific figure actions; DocumentEvent → report;
CustomEvent → scoped custom instruction; StopEvent → session end;
ClusterEvent → future subtyping template; SelectModelEvent → validate;
AnalyzeSurvivalEvent → survival template.

The legacy preprocessing prompt described scaling before the training split. The new workflow freezes
partitions first and records fitted training indexes. Legacy outputs do not establish end-to-end agent
execution; this implementation and its future runs must be identified separately in revision evidence.
