# DECISIONS

## 1. Who is the user, and what do they need?

The user is an engineer at a crane company. When a customer asks for a crane, the engineer needs to send them a first drawing quickly, with the main sizes and technical data, so the customer can check that the crane fits their building. Drawing this by hand takes time; the app makes it in about a minute.

## 2. What did you assume (crane type, inputs, units, ranges), and why?

- **Crane type:** single girder overhead (EOT) crane, because the reference drawing shows this type and it is the simplest common type.
- **Inputs:** load, span and lifting height, because they are the first three lines of the technical data on the reference drawing and they decide the main sizes.
- **Units:** millimetres and tonnes, the same as the reference drawing.
- **Ranges:** load 1–20 t, span 5–30 m, lifting height 3–20 m. These are guesses, not from a standard. The reference crane (10 t, 25 m, 7.9 m) is inside them.

## 3. Where did each formula or rule come from, and how sure are you?

All fixed sizes come from the one reference drawing:

- Rail top = lifting height + 810 (8710 − 7900 on the drawing)
- Min. building height = rail top + 1369 (crane height above rail) + 200 (roof clearance)
- Overall crane length = span + 270 (25270 − 25000)
- Min. 235 mm from the crane end to the wall, wheelbase 3800 mm, end carriage 4310 mm

I am sure they match the reference crane (10 t, 25 m). For other sizes I am not sure: a real smaller or bigger crane would have different numbers. That is why every such size is marked "(est.)" and the drawing says "Preliminary – not for construction".

## 4. What did you leave out on purpose?

- **Login:** not needed for a first version.
- **Strength checks** (beam strength, deflection, wheel loads): I do not have the engineering rules, and a wrong check is worse than no check.
- **Side view (section A-A), hook approach distances, speeds, power and weights:** they need data I do not have.
- **Other crane types** (double girder, gantry) and **PDF/DXF export:** to keep the scope small.

## 5. What three questions would you ask our engineers?

1. Can you give me the real technical specs for cranes of different sizes, so the sizes I copied from one drawing (like 1369 mm and 810 mm) can change with load and span?
2. What load, span and lifting height ranges do your customers really order, and at what size do you switch from a single girder to a double girder crane?
3. What must a first drawing for a customer always show (for example hook approach distances, wheel loads, a side view), and what can be left out?

## 6. What would you do with another week?

- Replace the sizes copied from the one reference drawing with real rules or tables from your engineers, so the drawing changes correctly with load and span.
- Add the hook approach distances (Min.920 / Min.1150 on the reference drawing) and a simple side view (section A-A).
- Add basic checks such as wheel load and beam deflection, and a PDF export.
- Add automated tests for the API and the drawing.

---