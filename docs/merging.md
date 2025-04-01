Have component (C) with template and connections, where a connection specifies a template port
and a node with which to identify the connection.

```
                                C              C
                               --- u_GastricC ---
                 C           /                    \
     -- u_Aorta --- u_CeliacA                      u_PortalV --
                             \\                    /
                               --- u_SplenicC ---
                                C              C


C ==>  --> U --> V --> U -->


                             --> G --> V --> P -->
                 --> C --> V --> G -->
     --> A --> V --> C -->
                 --> C --> V --> S -->
                             --> S --> V --> P -->



                         - V --> G -->
                        /              V
     --> A --> V --> C                   --> P -->
                      \\               V
                        -- V --> S -->



v_in ---> U_node1 --> V_segment --> U_node2 ---> v_out
```
