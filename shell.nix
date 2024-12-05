
# This shell.nix provides a simple development environment for the btnl_client python package.
#
# First, run `nix-shell` to get into the development environment:
#
# $ nix-shell
#
# From within this Nix shell, you can run the `bntl_client` module like the
# following to play around with it:
#
# $ python -m btnl_client
#
# Here is an example of running one of the available subcommands.  This gets
# the specifications for a Product:
#
# $ python -m btnl_client get-product-spec 3
# ProductSpreadSpec(type='spread', product_id=3, product_name='Bitcoin US Dollar Calendar Spread', ...

{...}:

let
  nixpkgs-src = builtins.fetchTarball {
    # nixos-unstable as of 2023-08-11
    url = "https://github.com/NixOS/nixpkgs/archive/ce5e4a6ef2e59d89a971bc434ca8ca222b9c7f5e.tar.gz";
    # obtained with 'nix-prefetch-url --unpack <url>'
    sha256 = "16ls4izhj8jwm8s4ydjma6ghr76xxrclcw86iy4id3bm9i60n8l1";
  };

  pkgs = import nixpkgs-src {};

  python-with-my-packages =
    pkgs.python39.withPackages
      (python-pkgs:
        [ python-pkgs.pytest
          python-pkgs.build
          #python-pkgs.python-lsp-server

          # Add your other dependencies here
          python-pkgs.requests
          python-pkgs.types-requests
          python-pkgs.websockets
        ]
      );
in
pkgs.stdenv.mkDerivation {
  name = "python-btnl-client";
  buildInputs = [
    python-with-my-packages

    # Add other non-python dependencies here
    pkgs.which
  ];
}
