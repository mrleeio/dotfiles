# PostgreSQL 18 Configuration
# postgresql@18 is keg-only, so we need to add it to PATH manually

export PATH="/opt/homebrew/opt/postgresql@18/bin:$PATH"

# Compiler flags for building against PostgreSQL
export LDFLAGS="-L/opt/homebrew/opt/postgresql@18/lib $LDFLAGS"
export CPPFLAGS="-I/opt/homebrew/opt/postgresql@18/include $CPPFLAGS"

# To start PostgreSQL:
#   brew services start postgresql@18
# Or run manually:
#   LC_ALL="en_US.UTF-8" /opt/homebrew/opt/postgresql@18/bin/postgres -D /opt/homebrew/var/postgresql@18
