# Generated wrapper for the same Python artifact; no bundled ML dependency tree.
class Mlca < Formula
  desc "Guided machine learning workflows with recorded provenance"
  homepage "https://github.com/OWNER/REPOSITORY"
  url "https://files.pythonhosted.org/packages/source/m/mlca/mlca-0.2.0.tar.gz"
  sha256 "a4e48a4ac36605eee88c5733d1b384d4faecef82f00dad7e5886e364547db607"
  version "0.2.0"

  depends_on "uv"

  def install
    (bin/"mlca").write <<~EOS
      #!/bin/sh
      exec "#{Formula["uv"].opt_bin}/uv" tool run --from "mlca==0.2.0" mlca "$@"
    EOS
  end

  test do
    assert_match "0.2.0", shell_output("#{bin}/mlca --version")
  end
end
