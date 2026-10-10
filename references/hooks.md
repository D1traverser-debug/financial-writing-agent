# Reader Funnel / Hook module

## Objective
Optimize the complete reading funnel for publishable financial writing:
**qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered**.

Do not optimize one surface in isolation. A title that raises clicks but attracts the wrong reader, an opening that withholds too much, or H1s that promise more than the article can support are funnel failures even if one metric improves.

The reader profile is an input, not a stereotype. The currently known audience skews toward readers around 45 with a substantial 55+ group. This supports clearer signposting, readable density and low avoidable cognitive friction, but it does not justify simplifying the analysis or assuming lower sophistication. Account-level behavior outranks generic demographic assumptions.

## Dedicated Reader Funnel / Hook Gate
This remains a separate semantic gate from general editorial quality and Natural Authorial Prose. The frozen draft is judged on the funnel as one system.

### 1. Audience-promise fit
Before optimizing click-through rate, identify **who this version is for and what useful understanding they expect from it**.

- `FINANCE_DEEP`: prioritize qualified finance readers who value complete explanation.
- `FINANCE_BROAD`: broader finance relevance matters more. The reader should not need pre-existing interest in the niche industry. Surface the financially consequential stake early: profit, orders, cash flow, capital expenditure, asset/company differentiation, policy transmission or another evidence-backed money consequence.

A broad finance article is not defined by “mentioning stocks” or by adding hype to an industry report. It translates a sector event into a question about **where money, orders, profits, cash flow or valuation-relevant differences are moving, and which companies are economically different**.

“Cross-industry finance clickability” remains optional: do not bolt on unrelated macro or market themes merely to widen reach. But `FINANCE_BROAD` normally fails audience fit if the title/opening assumes the reader already cares about the sector and never exposes a non-niche financial stake.

### 2. Headline information value
A title should reveal enough concrete information for the intended reader to understand why the article is worth attention. Prefer identifiable entities/events plus a real financial stake over generic suspense.

The title should answer at least part of: **what changed, why it matters financially, who/what may be differentiated, or what important distinction the article will resolve**.

Avoid titles whose only force comes from adjectives, hype, mystery or emotional pressure.

For `FINANCE_BROAD`, a stronger title may use sharper contrast, a larger information gap or more salient money language than `FINANCE_DEEP`, provided every implication is supported by the body. “More clickable” means a stronger truthful stake, not fabricated urgency, guaranteed return language or vague sensationalism.

### 3. Curiosity / concreteness balance
Do not maximize curiosity by maximizing vagueness. The useful target is an **information gap with a visible payoff**: enough specificity to establish relevance and credibility, enough incompleteness to leave a material question worth resolving.

Question headlines are not automatically stronger. Use a question only when the question itself is the clearest, most information-bearing framing for this topic.

A high-click/low-completion headline is not a success. If the title promise outruns the body's evidence or attracts readers for the wrong reason, revise the title rather than defending raw CTR.

### 4. Headline strategy diversity — pool-level hard gate
A pool of 8–12 unique strings is not enough. The candidates must represent **different supported strategies**, encoded through `angle_family`.

Use at least five genuinely distinct families when applicable, such as:
- `hard_fact` — concrete event/project/order/price change;
- `profit_orders` — orders, revenue, margin, cash-flow realization;
- `supply_demand` — capacity, supply constraints, price/volume balance;
- `company_divergence` — why beneficiaries differ economically;
- `policy_transmission` — policy to project/order/earnings chain;
- `expectation_gap` — observable fact versus market/industry expectation;
- `valuation_capital` — valuation, capex, capital-allocation consequence;
- `global_comparison` — domestic/overseas timing or competitive contrast;
- `validation_risk` — what evidence would confirm/falsify the thesis;
- `market_selection` — only when price-formation scope is materially active.

Changing nouns inside the same rhetorical mold is **not** strategy diversity. A pool dominated by variants of:
- “真正的X，不在Y”；
- “X又动了，这次看什么”；
- “别只看X，要看Y”；
- generic “拐点来了？” questions
fails even if every title is technically different.

The schema enforces a minimum number of angle families; the semantic judge still checks whether those labels reflect genuinely different reader-value propositions rather than cosmetic relabeling.

### 5. Selected-headline distinctiveness
The selected title must earn its click with topic-specific information. Generic formulae, empty colloquial questions, reusable suspense shells or slogans fail unless the user's own performance data specifically demonstrates that form works for this account and the body can honor the promise.

A strong title normally contains at least two of these three elements:
1. a concrete change/entity/event;
2. a financially consequential stake;
3. a real distinction/information gap.

Do not force all three if that makes the title cumbersome.

For `FINANCE_BROAD`, explicitly test the **cold-reader test**: would a finance reader with no prior interest in this industry still understand why the event could matter to money, profits, company differentiation or capital allocation from the title alone? If not, regenerate the title pool.

### 6. WeChat search discoverability
Search intent is independent from click appeal. Before title selection, perform current keyword reconnaissance instead of relying on a permanent remembered keyword list.

Prefer, when accessible:
1. the user's own public-account search/source terms and historical performance;
2. current WeChat Search / WeChat Index / search-suggestion evidence;
3. current Tencent/WeChat ecosystem evidence;
4. clearly labeled proxies when direct evidence is unavailable.

Record candidate terms and evidence references. Never invent exact search volume or call a term “high-frequency” without evidence. Use search terms naturally; keyword stuffing that weakens title clarity or reader fit is a failure.

### 7. First-three-sentence retention
Treat the first three complete sentences as the first payoff surface. They should naturally accomplish most of the following without becoming a fixed template:
- deliver a concrete change, fact or analytical payoff quickly;
- establish why the intended reader should care;
- begin paying off the title;
- create the next supported question, distinction or unresolved mechanism that the body will answer.

For `FINANCE_BROAD`, the first screen should normally translate sector jargon into the same non-niche financial stake promised by the title before diving into technical detail.

Do not spend the first screen on generic background, self-introduction, throat-clearing or a paraphrase of the headline.

### 8. Continuation flow: H1 + paragraph transitions
H1s and paragraph transitions are two parts of the same continuation mechanism.

Every H1 should be information-bearing and make the next section worth entering. Avoid generic labels such as “产业链梳理”“相关公司”“市场表现”“未来展望” unless the heading itself adds a finding, distinction or question.

Paragraph transitions must perform real work: cause, consequence, contrast, chronology, narrowing, comparison, correction or inference. A section should normally create the reason for the next section instead of ending as an isolated information block.

Visible numbered H2/H3 structure is welcome when it lowers cognitive cost; Reader Funnel judges whether it improves navigation, while Editorial owns whether the analytical branches require it.

### 9. Completion payoff
The article must still create value in its final substantive section. It should add information, close an earlier loop, establish validation/falsification conditions, resolve an important comparison or state what remains unresolved.

For stock/theme Deep articles, a final validation/monitoring section cannot retreat into a generic industry checklist if named-company implications are material. The reader should be able to connect the signal to the affected stock/class.

For multi-company topics, the completion payoff should leave the reader with an evidence-based comparison map—such as current realization visibility, operating sensitivity and what still needs validation—without turning that map into a trading instruction or disguised recommendation list.

Avoid recap-only endings. The risk/disclaimer should remain concise and topic-specific so it does not become an unnecessary dead zone before the comment area.

### 10. Title-opening payoff
The opening must promptly honor the strongest title promise. A curiosity gap is legal only if the article can close it with evidence. Bait-and-switch, unsupported superlatives and deliberately withholding the promised answer too long are failures.

## Headline candidate generation
For each applicable formal mode, generate 8–12 genuinely different candidates before selection. Each candidate records:
- target reader / reader job;
- `angle_family`;
- financial relevance;
- why that reader has a reason to click;
- the primary information gap;
- the promised payoff;
- cognitive load;
- current WeChat search terms and evidence refs;
- broader-finance relevance when genuinely useful.

Selection optimizes **qualified expected value**, not raw imagined CTR. A narrower title that attracts the right reader and produces stronger completion can beat a broader title that overpromises.

## Learning hierarchy
Use evidence in this order when refining funnel rules:
1. the user's explicit durable instruction;
2. the user's own account-level click, search, completion and feedback data;
3. repeated accepted edits / repeated performance patterns across articles;
4. current platform evidence and large-scale research;
5. generic writing heuristics.

Do not turn one successful article into a permanent formula.

## Audit evidence
A PASS must cite the final selected title, target-reader rationale, **candidate-pool strategy diversity**, actual first three sentences, representative H1/transition evidence, completion payoff and current search evidence. For `FINANCE_BROAD`, also cite the concrete non-niche financial stake exposed to a cold finance reader. “吸引人”“有钩子”“适合读者” without text-level or performance-level evidence is not an audit.
