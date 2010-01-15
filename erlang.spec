### RPM external erlang R12B_5
%define downloadv %(echo %realversion | tr _ -)
Source: http://erlang.org/download/otp_src_%{downloadv}.tar.gz
Requires: openssl

# 32-bit
Provides: libc.so.6(GLIBC_PRIVATE)
# 64-bit
Provides: libc.so.6(GLIBC_PRIVATE)(64bit)

%prep
%setup -n otp_src_%{downloadv}

%build
./configure --prefix=%i
make

%install
make install

export ERLANG_INSTALL_DIR=%i
cat %i/lib/erlang/bin/erl | sed "s,$ERLANG_INSTALL_DIR,\$ERLANG_ROOT,g" > %i/lib/erlang/bin/erl.new
mv %i/lib/erlang/bin/erl.new %i/lib/erlang/bin/erl
chmod a+x %i/lib/erlang/bin/erl

# SCRAM ToolBox toolfile
mkdir -p %i/etc/scram.d
cat << \EOF_TOOLFILE >%i/etc/scram.d/%n
<doc type=BuildSystem::ToolDoc version=1.0>
<Tool name=Erlang version=%{realver}>
<lib name=erlang>
<client>
 <Environment name=ERLANG_BASE default="%i"></Environment>
 <Environment name=INCLUDE default="$ERLANG_BASE/include"></Environment>
 <Environment name=LIBDIR  default="$ERLANG_BASE/lib"></Environment>
</client>
<Runtime name=PATH value="$ERLANG_BASE/bin" type=path>
</Tool>
EOF_TOOLFILE

# This will generate the correct dependencies-setup.sh/dependencies-setup.csh
# using the information found in the Requires statements of the different
# specs and their dependencies.
mkdir -p %i/etc/profile.d
echo '#!/bin/sh' > %{i}/etc/profile.d/dependencies-setup.sh
echo '#!/bin/tcsh' > %{i}/etc/profile.d/dependencies-setup.csh
echo requiredtools `echo %{requiredtools} | sed -e's|\s+| |;s|^\s+||'`
for tool in `echo %{requiredtools} | sed -e's|\s+| |;s|^\s+||'`
do
    case X$tool in
        Xdistcc|Xccache )
        ;;
        * )
            toolcap=`echo $tool | tr a-z- A-Z_`
            eval echo ". $`echo ${toolcap}_ROOT`/etc/profile.d/init.sh" >> %{i}/etc/profile.d/dependencies-setup.sh
            eval echo "source $`echo ${toolcap}_ROOT`/etc/profile.d/init.csh" >> %{i}/etc/profile.d/dependencies-setup.csh
        ;;
    esac
done
perl -p -i -e 's|\. /etc/profile\.d/init\.sh||' %{i}/etc/profile.d/dependencies-setup.sh
perl -p -i -e 's|source /etc/profile\.d/init\.csh||' %{i}/etc/profile.d/dependencies-setup.csh

%post
%{relocateConfig}etc/scram.d/%n
%{relocateConfig}etc/profile.d/dependencies-setup.sh
%{relocateConfig}etc/profile.d/dependencies-setup.csh

# setup approripate links and made post install procedure
. $RPM_INSTALL_PREFIX/%{pkgrel}/etc/profile.d/init.sh
rm -f $ERLANG_ROOT/bin/*
rm -f $ERLANG_ROOT/lib/erlang/bin/epmd
ln -s $ERLANG_ROOT/lib/erlang/erts-5.6.5/bin/epmd $ERLANG_ROOT/lib/erlang/bin/epmd
for pkg in dialyzer epmd erl erlc escript run_erl to_erl typer
do
    ln -s $ERLANG_ROOT/lib/erlang/bin/$pkg $ERLANG_ROOT/bin/$pkg
done

