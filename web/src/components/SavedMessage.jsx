function SavedMessage({ show, text }) {
  if (!show) return null;
  return <span className="text-helper text-success">{text}</span>;
}

export default SavedMessage;
