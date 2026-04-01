{
  description = "Python+UV development";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      lib = pkgs.lib;
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        # environment values previously computed in shell.nix
        NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
          pkgs.stdenv.cc.cc
          pkgs.zlib
        ];

        NIX_LD = lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";

        packages = with pkgs; [
          uv
          python313
        ];

        shellHook = ''
          export LD_LIBRARY_PATH="$NIX_LD_LIBRARY_PATH"
        '';
      };
    };
}
