import React, { useState } from "react";

function RemoveScoreboardButton({ onRemove }) {
  const [isModalOpen, setModalOpen] = useState(false);

  const openModal = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  const handleConfirm = () => {
    onRemove();
    closeModal();
  };

  return (
    <>
      <button className="remove-btn" onClick={openModal}>
        Remove Scoreboard
      </button>

      {isModalOpen && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div
            className="modal-content"
            onClick={e => e.stopPropagation()} // Stop click
          >
            <h2>Are you sure?</h2>
            <p>This will delete all scoreboard data.</p>
            <div className="modal-buttons">
              <button className="btn cancel" onClick={closeModal}>
                Cancel
              </button>
              <button className="btn confirm" onClick={handleConfirm}>
                Yes, delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default RemoveScoreboardButton;
