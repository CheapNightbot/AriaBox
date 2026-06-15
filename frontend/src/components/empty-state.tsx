function EmptyState() {
  return (
    <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
      <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
        Nothing to show here...⋆｡‧˚ʚ🧸ɞ˚‧｡⋆
      </p>
    </div>
  );
}

export default EmptyState;
