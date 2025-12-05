Hi Patryk,

The current performance thresholds are set to 0.70 for entity flagging and 0.60 for criminal labels. As noted in the documentation, these can be increased. I initially kept them lower to ensure consistent performance.

Entity flagging remains reliable at 0.90. For criminal labels, anything above 0.80 becomes challenging due to overlapping definitions between crimes. With that in mind, I suggest using 0.90 for entity flagging and 0.80 for criminal labels. Higher thresholds are possible but would require additional effort on our side.

You can find our prompt in utils/prompts.py.
