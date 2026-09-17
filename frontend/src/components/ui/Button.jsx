import './Button.css';

export default function Button({ variant = 'primary', as: Comp = 'button', className = '', ...props }) {
  return <Comp className={`btn btn-${variant} ${className}`} {...props} />;
}
