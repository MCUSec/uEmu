The KB format is shown in the following. The definition of each type please refer to our paper.

```
t0_addr_0x0_0x0_0x0
...
t1_addr_pc_hash_value ----------------------The hash of T1 only for backup in case it will upgrade to T2 during further round KB extration.
...
pt1_addr_pc_hash_value----------------------pt1 is a subclass of t1, which denotes the value of this register does not lead to any invalud states in this round KB extraction.
...
dt1_addr_pc_0x0_value-----------------------dt1 is also a subclass of t1, which denotes this registers has been read only once.
...
t2_addr_pc_hash_value
t2_addr_pc_hash_value
...
t3_addr_0x0_readingtime_value
...
tirqs_addr_pc_irqnumber_value --------------tirqs is a subclass of t1 and t2 type registers in IRQ handler which does not meet any t0 type registers in same IRQ handler.
...
IRQCR
tirqc_irqnumber_add_correspondingt0addr_correspondingt0value_value------------tirqc is a subclass of t1 and t2 type registers in IRQ handler which go with the value in t0 type registers in same IRQ handler.
...
Fuzzing
dfuzz_addr_width_countofreadingtimes -------defalut data register list
Recommd Fuzzing
rfuzz_addr_width_countofreadingtimes -------recommended data register list
```

