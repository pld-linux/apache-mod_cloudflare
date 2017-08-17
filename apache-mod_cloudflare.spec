%define		mod_name	cloudflare
%define 	apxs		%{_sbindir}/apxs
Summary:	Apache module to show true visitor IPs in logs for domains using CloudFlare
Name:		apache-mod_%{mod_name}
Version:	2016.10.0
Release:	1
License:	Apache v2.0
Group:		Networking/Daemons/HTTP
Source0:	https://github.com/cloudflare/mod_cloudflare/archive/98ab38a/mod_%{mod_name}-%{version}.tar.gz
# Source0-md5:	d618e95ba37e48139858ebadc908b142
Source1:	apache.conf
URL:		https://github.com/cloudflare/mod_cloudflare
BuildRequires:	apache-devel >= 2.2
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	apache(modules-api) = %apache_modules_api
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)/conf.d

%description
CloudFlare acts as a proxy, which means that your visitors are routed
through the CloudFlare network and you do not see their original IP
address.

This module uses HTTP headers provided by the CloudFlare proxy to log
the real IP address of the visitor. Based on mod_remoteip.c, this
apache extension will replace the remote_ip variable in user's logs
with the correct remote_ip sent from CloudFlare. This also does
authentication, only performing the switch for requests originating
from CloudFlare IPs.

%prep
%setup -qc
mv mod_cloudflare-*/* .

%build
. ./VERSION
version=$MAJOR.$MINOR.$BUILD
test "$version" = %{version}

%{apxs} -c mod_%{mod_name}.c

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}}

%{apxs} -i -S LIBEXECDIR=$RPM_BUILD_ROOT%{_pkglibdir} -n 'mod_cloudflare' mod_cloudflare.la

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/90_mod_%{mod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%doc README.md
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/mod_%{mod_name}.so
