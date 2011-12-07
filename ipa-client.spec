%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%global POLICYCOREUTILSVER 2.0.82-13
%global gettext_domain ipa
%global UPSTREAM_RELEASE 1.9.0.pre3

Name:           ipa-client
Version:        2.0
Release:        9%{?date}%{?dist}
Summary:        IPA authentication for use on clients

Group:          System Environment/Base
License:        GPLv2
URL:            http://www.freeipa.org/
Source0:        http://www.freeipa.org/downloads/src/freeipa-%{UPSTREAM_RELEASE}.tar.gz
Patch1:         ipa-client-install.patch
Patch2:         ipa-client-binaries.patch
Patch3:         ipa-client-nokrbv.patch
Patch4:         ipa-client-nslcd.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  openldap-devel
BuildRequires:  krb5-devel
BuildRequires:  python-devel
BuildRequires:  python-setuptools
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  popt-devel
BuildRequires:  m4
BuildRequires:  xmlrpc-c-devel
BuildRequires:  curl-devel
BuildRequires:  gettext

Requires: python-ldap
Requires: cyrus-sasl-gssapi
Requires: ntp
Requires: krb5-workstation
Requires: authconfig
Requires: pam_krb5
Requires: nss-pam-ldapd
Requires: wget
Requires: sssd
Requires: certmonger
Requires: policycoreutils >= %{POLICYCOREUTILSVER}
Requires: authconfig

%description
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof).

%prep
%setup -n freeipa-%{UPSTREAM_RELEASE} -q
%patch1 -p1 -b .ipa-client
%patch2 -p1 -b .binaries
%patch3 -p1 -b .nokrbv
%patch4 -p1 -b .nslcd

%build
export CFLAGS="$CFLAGS %{optflags}"
export CPPFLAGS="$CPPFLAGS %{optflags}"
make version-update
cd ipa-client; ../autogen.sh --prefix=%{_usr} --sysconfdir=%{_sysconfdir} --localstatedir=%{_localstatedir} --libdir=%{_libdir} --mandir=%{_mandir} --with-openldap; cd ..

make IPA_VERSION_IS_GIT_SNAPSHOT=no %{?_smp_mflags} client
cd selinux

%install
rm -rf %{buildroot}
make client-install DESTDIR=%{buildroot}

# The pot file currently just covers the main framework, not the client
# installer. These files are shipped with the ipa-python package. If we
# include them here we'll get a conflict if we try to install
# ipa-python from the server, so remove them.
%find_lang %{gettext_domain}
for file in `cat %{gettext_domain}.lang | awk '{ print$2 }'`
do
    rm -f %{buildroot}$file
done

mkdir -p %{buildroot}/%{_localstatedir}/lib/ipa-client/sysrestore

# Undo the ipa-python install and copy the files we need
mkdir %{buildroot}/%{python_sitelib}/ipaclient/ipapython
mv %{buildroot}/%{python_sitelib}/ipapython/sysrestore.* %{buildroot}/%{python_sitelib}/ipaclient/ipapython 
mv %{buildroot}/%{python_sitelib}/ipapython/ipautil.* %{buildroot}/%{python_sitelib}/ipaclient/ipapython 
mv %{buildroot}/%{python_sitelib}/ipapython/version.* %{buildroot}/%{python_sitelib}/ipaclient/ipapython 
mv %{buildroot}/%{python_sitelib}/ipapython/dnsclient.* %{buildroot}/%{python_sitelib}/ipaclient/ipapython 
mv %{buildroot}/%{python_sitelib}/ipapython/ipavalidate.* %{buildroot}/%{python_sitelib}/ipaclient/ipapython 
mv %{buildroot}/%{python_sitelib}/ipapython/config.* %{buildroot}/%{python_sitelib}/ipaclient/ipapython 
mv %{buildroot}/%{python_sitelib}/ipapython/__init__.* %{buildroot}/%{python_sitelib}/ipaclient/ipapython 

rm -rf %{buildroot}/%{python_sitelib}/ipapython
rm -rf %{buildroot}/%{python_sitelib}/ipalib
rm -rf %{buildroot}/%{python_sitelib}/*.egg-info

# So we can own our configuration file
mkdir -p %{buildroot}/%{_sysconfdir}/ipa
/bin/touch %{buildroot}/%{_sysconfdir}/ipa/default.conf

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc LICENSE README
%{_sbindir}/ipa-client-install
%{_sbindir}/ipa-getkeytab
%{_sbindir}/ipa-rmkeytab
%{_sbindir}/ipa-join
%dir %{_usr}/share/ipa
%dir %{_usr}/share/ipa/ipaclient
%dir %{_localstatedir}/lib/ipa-client
%dir %{_localstatedir}/lib/ipa-client/sysrestore
%{_usr}/share/ipa/ipaclient/ipa.cfg
%{_usr}/share/ipa/ipaclient/ipa.js
%dir %{python_sitelib}/ipaclient
%dir %{python_sitelib}/ipaclient/ipapython
%{python_sitelib}/ipaclient/*.py*
%{python_sitelib}/ipaclient/ipapython/*.py*
%{_mandir}/man1/ipa-getkeytab.1.gz
%{_mandir}/man1/ipa-rmkeytab.1.gz
%{_mandir}/man1/ipa-client-install.1.gz
%{_mandir}/man1/ipa-join.1.gz
%ghost %config(noreplace) %{_sysconfdir}/ipa/default.conf

%changelog
* Tue Jun 22 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-9
- Add /etc/pam_ldap.conf to the list of files we update (#559004)

* Thu Jun  3 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-8
- Re-add patch to attempt to configure a number of nss_ldap related files
  if installed and configure nslcd.conf if installed. This got inadvertantly
  dropped when the source tarball was re-based (#559004)
- Update nokrbv patch to remove another usage of python-krbV that
  isn't directly used by ipa-client but fails at runtime. (#598626)

* Thu Jun  3 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-7
- Update nokrbv patch to remove another usage of python-krbV that
  isn't directly used by ipa-client but fails the build. (#598626)

* Thu Jun  3 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-6
- Remove dependency on python-krbV package (#598626)

* Mon May 10 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-5
- Add gettext as a BuildRequires (#556620)

* Thu May  6 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-4
- Update source tarball to freeIPA v2.0 alpha 3 (tag 1.9.0_alpha3) (#556620)
- More spec file clean ups
- Don't install the po files so it doesn't conflict with the server
  ipa-python package

* Fri Feb 19 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-3
- Remove explicit requires on krb5-libs (#556620)

* Wed Jan 27 2010 Rob Crittenden <rcritten@redhat.com> - 2.0-2
- Remove some commented-out Requires
- Replace Requires on nss_ldap with nss-pam-ldapd (#559004)
- Add patch to attempt to configure a number of nss_ldap related files
  if installed and configure nslcd.conf if installed (#559004)

* Wed Dec  2 2009 Rob Crittenden <rcritten@redhat.com> - 2.0-1
- Initial spec
- policycoreutils version set to 2.0.78-3 to fix problem with
  restorecon returning 1 in non-failure cases.
