import Card from '../components/ui/Card';
import './About.css';

const steps = [
  {
    title: 'Describe how you feel',
    body: 'Tell the assistant what you\'re experiencing, in your own words — no forms, no dropdowns.',
  },
  {
    title: 'It checks against real data',
    body: 'Your message is matched against curated symptom, condition, and precaution datasets to ground the response in something more than a guess.',
  },
  {
    title: 'You get a plain-language starting point',
    body: 'A clear next step — what it might be, what tends to help, and when it\'s worth seeing someone in person.',
  },
];

export default function About() {
  return (
    <section className="about-page">
      <div className="about-intro">
        <h1>Built to make sense of symptoms, not replace a doctor</h1>
        <p>
          Most symptom checkers either overwhelm you with a wall of possible
          conditions, or oversimplify into a single scary guess. AI Health Check
          aims for something more useful: a conversation that stays grounded in
          real data and tells you plainly what to do next.
        </p>
      </div>

      <div className="about-steps">
        {steps.map((step, i) => (
          <Card key={step.title} className="about-step">
            <span className="about-step-number">{i + 1}</span>
            <h3>{step.title}</h3>
            <p>{step.body}</p>
          </Card>
        ))}
      </div>

      <Card className="about-limits">
        <h3>What this isn't</h3>
        <p>
          It's a starting point for understanding what you're experiencing, built
          on local datasets and a locally-run language model — not a diagnosis,
          not a prescription, and not a replacement for a doctor's judgment. If
          something feels urgent, please contact a medical professional directly.
        </p>
      </Card>
    </section>
  );
}
