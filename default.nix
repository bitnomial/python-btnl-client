with import <nixpkgs> { };

let
  btnl-client-packages = python-packages: with python-packages; [
    pytest
    python-lsp-server
    build
    # Add your other dependencies here
    requests
    types-requests
  ];

  python-with-my-packages = python39.withPackages btnl-client-packages;

in
stdenv.mkDerivation {
  name = "python-btnl-client";
  buildInputs = [
    python-with-my-packages
    # Add other non-python dependencies here
    which
  ];
}
