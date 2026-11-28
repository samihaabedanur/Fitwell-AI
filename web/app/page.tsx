import Link from "next/link";

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="label">Fitwell</div>
        <h1>Find every material in your mood board, and the real ones that match.</h1>
        <p>Upload a board or a single sample. Fitwell cuts out each material, groups similar ones, and shows five
          close matches from 3,246 materials, each with a material passport.</p>
      </section>
      <section className="grid">
        <article className="card">
          <div className="label">Upload</div>
          <h2>Mood board</h2>
          <p>Every material on the board, grouped, with matches and passports. Objects such as lamps and labels are set aside.</p>
          <Link className="btn" href="/moodboard">Analyse a mood board</Link>
        </article>
        <article className="card">
          <div className="label">Upload</div>
          <h2>Single material</h2>
          <p>A photo of one surface or sample: what it is, and five similar materials with passports.</p>
          <Link className="btn" href="/material">Analyse a material</Link>
        </article>
        <article className="card">
          <div className="label">Plan</div>
          <h2>2D to 3D planner</h2>
          <p>Turn a floor plan into a 3D home and change the material of each wall, floor and ceiling.</p>
          <Link className="btn light" href="/planner">Open the 3D studio</Link>
        </article>
        <article className="card">
          <div className="label">Coming next</div>
          <h2>Room photo</h2>
          <p>Every material in a room photo, then a 3D room you can re-finish and furnish.</p>
          <span className="pill soft">In progress</span>
        </article>
      </section>
    </>
  );
}
