interface ButtonProps<T extends { readonly: boolean; deleted: boolean }> {
    item: T;
    onDelete: () => void;
    onRevert: () => void;
    enabled: boolean;
}

export function DeleteRevertButton<T extends { readonly: boolean; deleted: boolean }>({
    item,
    onDelete,
    onRevert,
    enabled,
}: ButtonProps<T>) {

    function handleClick() {
        if(!enabled) return;
        if (item.deleted) {
            onRevert();
        } else {
            onDelete();
        }
    }

    if (item.readonly) {
      return (
        <button
            className="shrink-0 bg-gray-400 p-1.5 text-[12px] text-dark-blue rounded-lg w-15"
            onClick={() => {}}>
                {/* <span className="opacity-0">Bloqueado</span> */}
            </button>
        );
    };

  return item.deleted ? (
    <button
        className="shrink-0 bg-white p-1.5 text-[12px] text-dark-blue rounded-lg border-2 border-dark-blue"
        onClick={handleClick}>Reverter</button>
    ) : (
    <button
        className="shrink-0 bg-burnt-red p-1.5 text-[12px] text-white rounded-lg border-2 border-burnt-red"
        onClick={handleClick}>Remover</button>
    );
}
