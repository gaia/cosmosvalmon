# Cosmos validator missed block monitor/alerts

time, block height, block proposer ID, number of validators that missed the block

![Sample Output](https://i.imgur.com/dMWoVJD.png)

- Tracks how many Cosmos validators missed a block
- Optionally alerts if your validator is one of those that missed the block
- Logs your missed blocks to disk. You can analyze this log to try to infer where you'd place your next sentry.

If your validator missed the block, it appends "(including your validator)." If the number of validators that missed is below your threshold (alertIfLessThan) it will send an alert and further append "X validators missed, below your threshold of Y".

To sort from which proposer your validator misses the most blocks, use `cat /path/to/log/txt | cut -f 3 -d ',' | sort| uniq -c |sort -nr` on the log (disk log, not journalctl) output.

This is my first piece of Python, all feedback is welcome.
