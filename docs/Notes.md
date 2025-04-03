# Notes

## 19 March 2025

### Circulatory Autogen

A project to generate and calibrate CellML circulatory system models from an array of module/vessel names and connections: [GitHub](https://github.com/FinbarArgus/circulatory_autogen).

## 16 January 2025

### Constructing branching (vascular) models from templates.

There are two separate sets of RDF:

1.  Template descriptions, such as [vascular-segment-template.ttl](../data/vascular-segment-template.ttl), which is a description of the basic model below, are intended to be used
    by model generation tools for both validation and generation.
2.  Model definitions specify both template interconnections and model parameters and states (quantities). The examples [single-segment.ttl](../data/single-segment.ttl)
    and [stomach-spleen.ttl](../data/stomach-spleen.ttl) use `vascular-segment-template.ttl` to respectively define a single segment 
    and a branching network (representing the stomach/spleen vasculature).

Shape expressions are used to validate RDF structure:

1.  [template.shex](../data/shex/template.shex) for template descriptions.
2.  [bgmodel.shex](../data/shex/bgmodel.shex) for model definitions. 

> [!NOTE]
> The above shape expression files are out-of-date and can't be used to validate the examples.

### Validating RDF against shape expressions

```
poetry shell
shexeval -A models/template.ttl shex/template.shex
shexeval -A models/vascular.ttl shex/bgmodel.shex
```


## Email from PH, 11 December 2024 3:41 pm

I’ve been thinking a bit more about this and wonder if we should simplify it a bit further.

If the basic module is:

![](./images/image001.png)

the boundary conditions can be specified as either or at the LH end and either or at the RH end. Serial additions or bifurcations are straightforward:

![](./images/image014.png)

And insertion of a more complex network is:

![](./images/image015.png)
