import { PLANNER_URL } from "@/lib/config";

export default function PlannerPage() {
  const planner = PLANNER_URL || "https://samihaabedanur.github.io/Fitwell-AI/docs/editor.html";
  return (
    <section className="studio-frame">
      <div className="label">Fitwell Studio</div>
      <h1>Build your room in 3D.</h1>
      <p className="status">Draw a scaled floor, add walls and partitions, place windows, curtains, furniture, and materials.</p>
      <iframe title="Fitwell 3D Studio" src={planner} allow="fullscreen" />
    </section>
  );
}
