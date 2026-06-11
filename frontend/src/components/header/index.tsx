import "./header.css";

function Header() {
  return (
    <header className="text-center">
      <h1
        id="header-logo"
        className="p-4 select-none text-3xl font-semibold tracking-wide mb-2 hover:cursor-pointer"
        onClick={() => (window.location.href = "/")}
      >
        AriaBox ⨾<span className="rotate">💿</span>✮˚.⋆
      </h1>
    </header>
  );
}

export default Header;
