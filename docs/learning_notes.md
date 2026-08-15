# Learning Notes

These are notes from things I had to stop and think about while building this project.

They are not meant to be a dbt tutorial or a complete reference. I am keeping them mainly so I can remember why I made certain decisions and revisit concepts that were not obvious to me at first.

---

# Day 3 — dbt, modelling and data quality

## How I ended up with staging → intermediate → ML

When I started reorganising the project with dbt, one of the first things I was unsure about was how the models should actually be structured.

There are a lot of terms around data modelling — staging, marts, Kimball, Data Vault, intermediate models — and initially I was mixing some of them together.

For this project I ended up with:

```text
raw_severe_injuries
        ↓
stg_severe_injuries
        ↓
int_injury_cases
        ↓
ml_injury_features
```

The reasoning is fairly simple.

`raw_severe_injuries` is the data as it enters DuckDB. dbt does not create it, so from dbt's point of view it is a source.

`stg_severe_injuries` stays close to that source. This is where I rename columns, cast types, parse dates and generally make the raw data easier to work with.

`int_injury_cases` is where the data starts to represent the concept I actually care about: an injury case. It contains derived information such as the year, month, NAICS levels and the target I will later use for ML.

Finally, `ml_injury_features` exists for one specific consumer: the Machine Learning code.

The distinction I want to remember is:

```text
staging
    source-oriented

intermediate
    reusable transformation and business logic

ml
    consumer-oriented
```

I initially also created a `marts` folder because that is common in dbt projects.

For now I am leaving it empty.

There is no point creating a mart just so that the repository looks like a standard dbt repository. If I later build an analytical use case or dashboard that needs a business-facing dataset, then a mart will have a real reason to exist.

---

## Why I did not use Data Vault here

I also wondered whether I should use Data Vault.

The project currently has one main source and a relatively simple objective.

I am not integrating several operational systems, maintaining complex histories across sources or trying to create an enterprise integration layer.

Adding hubs, links and satellites would therefore make the project more complicated without solving a problem I actually have.

This was a useful reminder:

> Knowing a modelling technique is not the same thing as needing to use it.

The current dbt structure and Data Vault are also not really alternatives at the same level.

`staging → intermediate → marts` is mainly about how transformations are organised inside a dbt project.

Data Vault is a data modelling methodology that could be part of a much larger architecture.

For example, another system could have:

```text
Sources
   ↓
Raw
   ↓
Data Vault
   ↓
Business transformations
   ↓
Dimensional marts
```

That is simply more architecture than this project currently needs.

---

## This project is ELT, not ETL

Another distinction that became clearer while doing this was ETL vs ELT.

Here I first load the OSHA data into DuckDB:

```text
OSHA CSV
   ↓
DuckDB
```

and only afterwards perform the transformations with dbt:

```text
DuckDB raw table
   ↓
dbt
   ↓
staging / intermediate / ML
```

So the order is:

```text
Extract
Load
Transform
```

which makes this an ELT pipeline.

The fact that Python is involved in ingestion does not make it ETL.

What matters is whether the transformation happens before or after loading the source data into the target data platform.

---

## `source()` and `ref()` finally made more sense

Initially I wondered why I needed:

```sql
from {{ source('osha', 'raw_severe_injuries') }}
```

instead of simply writing:

```sql
from raw_severe_injuries
```

The important part is not that dbt requires some special replacement for SQL table names.

It is that I am telling dbt what the relation represents.

The raw OSHA table exists independently of dbt, so I declare it using:

```text
source()
```

Once dbt creates a model itself, downstream models reference it using:

```text
ref()
```

In this project:

```text
raw_severe_injuries
        ↓ source()
stg_severe_injuries
        ↓ ref()
int_injury_cases
        ↓ ref()
ml_injury_features
```

This is also how dbt can understand the dependencies and construct the DAG.

One thing I initially mixed up was `ref()` with how SQL gets physically executed.

`ref()` does not mean that dbt recalculates an upstream model every time I query something.

It defines the dependency between models.

Whether the database has to evaluate upstream SQL again depends on how those models are materialized.

---

## Views were not quite what I had in my head

I knew what a SQL view was before this project, but I had never really stopped to think about what happens when several views depend on each other.

A view normally stores the SQL definition, not the resulting rows.

For example:

```text
raw table
    ↓
staging view
    ↓
intermediate view
```

If I query the intermediate view, the database may need to resolve the SQL behind the intermediate view and then the SQL behind the staging view before reaching the underlying table.

The intermediate view does not contain a frozen copy of those rows.

A table is different.

When dbt materializes a model as a table, the transformation is executed and the result is stored.

The trade-off now makes more sense to me:

```text
VIEW

cheap to create
reflects current upstream data
work may happen when queried
```

versus:

```text
TABLE

work happens when it is built
resulting rows are stored
cheap to consume afterwards
can become stale until rebuilt
```

That also helped me understand why the ML dataset makes sense as a table.

Model training will consume the same prepared dataset repeatedly.

Having a stable, materialized version of that dataset is useful.

For the relatively small staging and intermediate transformations in this project, views are enough.

---

## Where ephemeral and incremental fit

While looking at dbt materializations I also wanted to understand `ephemeral` and `incremental`.

An ephemeral model does not become a table or view in the database.

Its SQL is effectively incorporated into downstream models during compilation.

So instead of creating something like:

```text
database
└── some_intermediate_model
```

it behaves more like reusable SQL that becomes part of another model.

I do not currently need this in the project, but the distinction is useful.

An incremental model is still a table.

The difference is that after the initial build, dbt can be configured to process only new or changed data rather than rebuilding the complete table each time.

The progression I currently use as a mental model is:

```text
view
  ↓
querying becomes too expensive

table
  ↓
rebuilding becomes too expensive

incremental
```

It is not a strict rule.

It is just a useful way to think about when additional complexity might become justified.

---

## `dbt run`, `dbt test`, `dbt build` and `dbt parse`

The command names confused me a little at first.

In particular, `dbt run` also builds tables and views even though another command is called `dbt build`.

The simplified version I want to remember is:

```text
dbt run
    build the models

dbt test
    run the data tests

dbt build
    build and validate resources following the DAG

dbt parse
    read and understand the dbt project
```

### `dbt run`

`dbt run` executes the model SQL and materializes each model according to its configuration.

For this project:

```text
stg_severe_injuries   → VIEW
int_injury_cases      → VIEW
ml_injury_features    → TABLE
```

### `dbt test`

`dbt test` runs the assertions I have defined about the data.

For example:

```text
incident_id
    must not be null

event_date
    must not be null

high_severity_outcome
    must be 0 or 1
```

### `dbt build`

`dbt build` is what I use when I want to validate the pipeline more completely.

It builds resources and runs their associated tests while following the dependency graph.

That DAG-aware behaviour matters because invalid upstream data should not simply flow into downstream datasets.

Conceptually:

```text
staging
   ↓
test
   ↓
intermediate
   ↓
test
   ↓
ML dataset
```

### `dbt parse`

`dbt parse` is different because it is mostly about the project definition itself.

It reads configuration, SQL models, YAML, Jinja and dependencies and builds dbt's internal representation of the project.

It does not rebuild my DuckDB models.

When I saw:

```text
Performance info: target/perf_info.json
```

after running `dbt parse`, I initially wondered whether this was something important for the actual pipeline.

It is only information about dbt's parsing performance.

It can be useful for debugging dbt itself or investigating performance in a large project, but it is not part of the dataset or ML pipeline.

---

## Logical layers and materializations are different decisions

Another thing that became clearer was that:

```text
staging
intermediate
ml
marts
```

and:

```text
view
table
incremental
ephemeral
```

describe different things.

The first group describes the **responsibility of a model**.

The second describes **how that model physically exists or is compiled**.

For example, saying:

```text
intermediate model
```

does not automatically mean:

```text
view
```

A large or expensive intermediate model could perfectly well need to be a table.

Likewise, a mart does not automatically have to be a table.

The materialization depends on how the data is used.

---

## Grain was more important than I expected

Another concept I wanted to properly understand was grain.

The most useful question is:

> What exactly does one row represent?

For `int_injury_cases`, my answer is:

> One row represents one OSHA Severe Injury Report.

That sounds simple, but once the grain is clear it becomes much easier to reason about keys, duplicates and aggregations.

It also stopped me from assuming that a column called `ID` must automatically be the unique key.

---

## The uniqueness test found a problem with my assumption

Initially I added a uniqueness test to:

```text
incident_id
```

because I assumed OSHA's `ID` uniquely identified a report.

The test failed.

There were five values that appeared twice.

Looking at the actual records showed that these were not duplicate incidents.

The same source ID could correspond to:

```text
different event date
different employer
different location
different injury
```

So the problem was not necessarily bad duplicate data.

My assumption about the source identifier was wrong.

Instead of forcing:

```text
incident_id = unique
```

I now test:

```text
incident_id = not null
```

and validate that:

```text
incident_id + event_date
```

is unique in the current dataset.

I deliberately say **in the current dataset**.

I have not established that OSHA formally guarantees this combination as a permanent global business key.

This was one of the most useful lessons from this part of the project:

> A failing data test does not always mean the data needs to be fixed. Sometimes the test is showing that the assumption behind the model is wrong.

---

## Why I did not just remove the repeated IDs

Once I found the repeated IDs, it would have been easy to use:

```sql
select distinct ...
```

or something based on:

```sql
row_number()
```

and keep only one row.

That would have made the uniqueness test pass.

It also would have deleted valid incidents.

The records had the same source ID but represented genuinely different events.

The process I want to remember is:

```text
test fails
    ↓
inspect the records
    ↓
understand why
    ↓
decide whether the data or the assumption is wrong
```

not:

```text
test fails
    ↓
remove rows until it passes
```

---

## Why test something that the SQL already seems to guarantee?

The target currently comes from logic like:

```sql
case
    when amputation_count > 0
      or loss_of_eye_count > 0
        then 1
    else 0
end
```

That appears to guarantee that:

```text
high_severity_outcome
```

can only contain:

```text
0 or 1
```

So at first it seemed slightly redundant to also test:

```text
not_null
accepted_values: [0, 1]
```

The reason it makes sense is that the test represents the **expected contract of the model**, not simply a check against the exact SQL implementation I happen to have today.

The implementation can change later.

The expectation remains:

```text
high_severity_outcome must contain only 0 or 1
```

---

## Why `final_narrative` is not in my baseline ML features

When creating `ml_injury_features`, I had to think about whether the free-text incident narrative should be included.

At first it sounds like a very useful feature because it contains a lot of information about what happened.

The problem is the target.

My current target is:

```text
1 = amputation or loss of an eye
0 = neither
```

A final incident narrative might literally say:

```text
the employee suffered an amputation
```

If the model sees that text while trying to predict whether the case involved an amputation, I may simply be giving it the answer.

That is target leakage.

For the first structured baseline I therefore exclude:

```text
amputation_count
loss_of_eye_count
final_narrative
```

The first two directly define the target.

The narrative may reveal it.

This does not mean the text is useless.

It could later be used for a separate NLP experiment where the modelling question and information available at prediction time are defined differently.

---

## What I currently understand about the target

The target is the value the supervised Machine Learning model is trying to predict.

For this project:

```text
y = high_severity_outcome
```

and the possible values are:

```text
0
1
```

The remaining input variables form:

```text
X
```

Conceptually:

```text
X
↓
model
↓
prediction of y
```

If a model later returns something like:

```text
probability = 0.78
```

that does not mean there is some objectively known 78% medical probability that an amputation will happen.

It means that, given the model and the input features, the model estimates a probability of `0.78` for class `1`.

If the classification threshold were:

```text
0.5
```

then:

```text
0.78 > 0.5
```

would result in:

```text
prediction = 1
```

The historical target and the model prediction are therefore different things:

```text
target
    what actually happened in the historical data

prediction
    what the model thinks will happen / which class the case belongs to
```

---

## Notes on embeddings

I also wanted to properly understand what people mean when they talk about embeddings.

An embedding model takes something such as text and maps it into a numerical vector.

Conceptually:

```text
"worker injured hand in machine"
                ↓
        embedding model
                ↓
[0.31, -0.85, 0.12, ...]
```

The individual dimensions are not normally things I can interpret manually as:

```text
dimension 1 = injury
dimension 2 = machine
dimension 3 = hand
```

The representation has been learned by the model during training.

Texts with similar meaning should end up relatively close to one another in the embedding space.

Similarity can then be measured with something such as cosine similarity.

An important distinction for this project is that:

```text
embeddings ≠ RAG
```

Embeddings could be used as features for an NLP classifier.

RAG is a different pattern where embeddings are commonly used to retrieve relevant external information before giving that context to an LLM.

For now neither is needed for the first structured baseline.

---

# Things I want to be able to explain without looking them up

At this point I should be able to explain in my own words:

- why this project uses ELT
- why I separated staging, intermediate and ML models
- why there is currently no mart
- why Data Vault would be unnecessary here
- the difference between `source()` and `ref()`
- the difference between logical dbt layers and materializations
- view vs table vs ephemeral vs incremental
- `dbt run` vs `dbt test` vs `dbt build` vs `dbt parse`
- what grain means
- why `incident_id` is not a unique key
- why I did not simply deduplicate the repeated IDs
- why tests can be useful even if the current SQL appears to guarantee the result
- what the ML target represents
- the difference between target and prediction
- what an embedding is at a high level
- why the final narrative is excluded from the first ML dataset
- what target leakage means in the context of this project

---

# Day 4 — Machine Learning

To be continued.