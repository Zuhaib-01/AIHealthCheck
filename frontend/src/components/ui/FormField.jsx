import './FormField.css';

export default function FormField({ label, id, ...inputProps }) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <input id={id} {...inputProps} />
    </div>
  );
}
