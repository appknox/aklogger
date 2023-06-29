use log::{debug, error, info, trace, warn, Level, Log, Metadata, Record};
use once_cell::sync::Lazy;
use pyo3::prelude::*;
use pyo3::types::PyString;
use std::ffi::CString;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::sync::Mutex;

fn get_level(level: &PyString) -> Level {
    match level.to_string().to_lowercase().as_str() {
        "debug" => Level::Debug,
        "error" => Level::Error,
        "warn" => Level::Warn,
        "info" => Level::Info,
        "trace" => Level::Trace,
        _ => Level::Error,
    }
}
struct State {
    level: Level,
    name: String,
    log_file: Option<String>,
    slack_token: Option<String>,
    slack_level: Level,
}

impl State {
    fn set_name(&mut self, name: String) {
        self.name = name;
    }

    fn set_level(&mut self, level: Level) {
        self.level = level;
    }

    fn set_slack_token(&mut self, slack_token: Option<String>) {
        self.slack_token = slack_token;
    }

    fn set_slack_level(&mut self, slack_level: Level) {
        self.slack_level = slack_level;
    }

    fn set_log_file(&mut self, log_file: Option<String>) {
        self.log_file = log_file.clone();
        if log_file.is_some() {
            let path = log_file.unwrap().to_string();
            let path = Path::new(path.as_str());
            if !path.exists() {
                File::create(path).unwrap();
            }
        }
    }
}

static STATE: Lazy<Mutex<State>> = Lazy::new(|| {
    Mutex::new(State {
        level: Level::Info,
        name: "aklogger".into(),
        slack_token: None,
        slack_level: Level::Info,
        log_file: None,
    })
});

struct AkLogger;

impl Log for AkLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= STATE.lock().unwrap().level
    }

    fn log(&self, record: &Record) {
        if self.enabled(record.metadata()) {
            let message = format!(
                "[{}] {} - {}",
                STATE.lock().unwrap().name,
                record.level(),
                record.args()
            );
            let message = CString::new(message).expect("CString::new failed");
            println!("{}", message.to_string_lossy());
            let log_file = &STATE.lock().unwrap();
            let log_file = log_file.log_file.as_ref();
            if log_file.is_some() {
                let path = log_file.unwrap().to_string();
                let path = Path::new(path.as_str());
                let mut file = File::options().write(true).append(true).open(path).unwrap();
                writeln!(file, "{}", message.to_string_lossy()).unwrap();
            }
        }
    }

    fn flush(&self) {}
}

static AK_LOGGER: AkLogger = AkLogger;

#[pyfunction]
fn info(msg: &PyString) {
    info!("{}", msg);
}

#[pyfunction]
fn warn(msg: &PyString) {
    warn!("{}", msg);
}

#[pyfunction]
fn trace(msg: &PyString) {
    trace!("{}", msg);
}

#[pyfunction]
fn error(msg: &PyString) {
    error!("{}", msg);
}

#[pyfunction]
fn debug(msg: &PyString) {
    debug!("{}", msg);
}

#[pyfunction]
fn set_name(name: &PyString) {
    STATE.lock().unwrap().set_name(name.to_string());
}

#[pyfunction]
fn set_level(level: &PyString) {
    STATE.lock().unwrap().set_level(get_level(level));
}

#[pyfunction]
fn set_slack_token(slack_token: &PyString) {
    STATE
        .lock()
        .unwrap()
        .set_slack_token(Some(slack_token.to_string()));
}

#[pyfunction]
fn set_slack_level(slack_level: &PyString) {
    STATE
        .lock()
        .unwrap()
        .set_slack_level(get_level(slack_level));
}

#[pyfunction]
fn set_log_file(log_file: &PyString) {
    STATE
        .lock()
        .unwrap()
        .set_log_file(Some(log_file.to_string()));
}

/*
#[pyfunction]
fn quick(data1: Option<PyObject>, data2: Option<PyObject>, data3: Option<PyObject>) {
    dbg!(data1, data2, data3);
}
*/
#[pyfunction]
fn tpl(summary: &PyString, details: &PyString) -> String {
    format!(
        "
=====================
{}
---------------------
{}
=====================
",
        summary, details
    )
}

#[pymodule]
fn aklogger(_py: Python, m: &PyModule) -> PyResult<()> {
    log::set_logger(&AK_LOGGER).unwrap();
    log::set_max_level(Level::Info.to_level_filter());
    m.add_function(wrap_pyfunction!(info, m)?)?;
    m.add_function(wrap_pyfunction!(error, m)?)?;
    m.add_function(wrap_pyfunction!(debug, m)?)?;
    m.add_function(wrap_pyfunction!(trace, m)?)?;
    m.add_function(wrap_pyfunction!(crate::warn, m)?)?;
    m.add_function(wrap_pyfunction!(set_name, m)?)?;
    m.add_function(wrap_pyfunction!(set_level, m)?)?;
    m.add_function(wrap_pyfunction!(set_slack_token, m)?)?;
    m.add_function(wrap_pyfunction!(set_slack_level, m)?)?;
    m.add_function(wrap_pyfunction!(set_log_file, m)?)?;
    m.add_function(wrap_pyfunction!(tpl, m)?)?;
    Ok(())
}

/*
#[neon::main]
fn init_rust_logging_lib_neon(
    mut cx: neon::prelude::Context,
) -> neon::result::JsResult<neon::types::JsUndefined> {
    init_logging();
    Ok(cx.undefined())
}
*/
