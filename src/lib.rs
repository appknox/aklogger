use log::{debug, error, info, kv::Key, trace, warn, Level, Log, Metadata, Record};
use once_cell::sync::Lazy;
use pyo3::prelude::*;
use pyo3::types::PyString;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION};
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
        log::set_max_level(level.to_level_filter());
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

impl AkLogger {
    fn is_slack_enabled(&self, level: Level) -> bool {
        level <= STATE.lock().unwrap().slack_level
    }
}
impl Log for AkLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= STATE.lock().unwrap().level
    }

    fn log(&self, record: &Record) {
        let kv = record.key_values();
        if self.enabled(record.metadata()) {
            let message = format!(
                "[{}] {} - {}",
                STATE.lock().unwrap().name,
                record.level(),
                record.args()
            );
            let message = CString::new(message).expect("CString::new failed");
            println!("{}", message.to_string_lossy());
            let state = STATE.lock().unwrap();
            let log_file = state.log_file.as_ref();
            if log_file.is_some() {
                let path = log_file.unwrap().to_string();
                let path = Path::new(path.as_str());
                let mut file = File::options().write(true).append(true).open(path).unwrap();
                writeln!(file, "{}", message.to_string_lossy()).unwrap();
            }
            if state.slack_token.is_some() {
                let force_push_slack = kv.get(Key::from_str("force_push_slack")).unwrap();
                let force_push_slack = force_push_slack.to_bool().unwrap();
                if force_push_slack || self.is_slack_enabled(record.metadata().level()) {
                    let channel = kv.get(Key::from_str("channel")).unwrap();
                    let channel = channel.to_borrowed_str().unwrap();
                    let mut headers = HeaderMap::new();
                    let token = state.slack_token.clone().unwrap();
                    let token = format!("Bearer {}", token);
                    headers.insert(
                        AUTHORIZATION,
                        HeaderValue::from_str(token.as_str()).unwrap(),
                    );
                    let client = reqwest::blocking::Client::new();
                    client
                        .post("https://slack.com/api/chat.postMessage")
                        .headers(headers)
                        .query(&[("text", message)])
                        .query(&[("channel", channel)])
                        .send()
                        .unwrap();
                }
            }
        }
    }

    fn flush(&self) {}
}

static AK_LOGGER: AkLogger = AkLogger;

fn get_message(summary: &PyString, details: Option<&PyString>) -> String {
    if details.is_some() {
        tpl(summary, details.unwrap())
    } else {
        summary.to_string()
    }
}

trait GetChannel {
    fn get_channel(&self) -> &str;
}

impl GetChannel for Option<&PyString> {
    fn get_channel(&self) -> &str {
        match self {
            Some(t) => t.to_str().unwrap_or("#error"),
            None => "#error",
        }
    }
}

trait GetBool {
    fn get_bool(&self) -> bool;
}

impl GetBool for Option<bool> {
    fn get_bool(&self) -> bool {
        self.unwrap_or(false)
    }
}

#[pyfunction]
fn info(
    summary: &PyString,
    details: Option<&PyString>,
    channel: Option<&PyString>,
    force_push_slack: Option<bool>,
) {
    info!(
        channel = channel.get_channel(),
        force_push_slack=force_push_slack.get_bool();
        "{}", get_message(summary, details)
    );
}

#[pyfunction]
fn warn(
    summary: &PyString,
    details: Option<&PyString>,
    channel: Option<&PyString>,
    force_push_slack: Option<bool>,
) {
    warn!(
        channel = channel.get_channel(),
        force_push_slack=force_push_slack.get_bool();
        "{}", get_message(summary, details)
    );
}

#[pyfunction]
fn trace(
    summary: &PyString,
    details: Option<&PyString>,
    channel: Option<&PyString>,
    force_push_slack: Option<bool>,
) {
    trace!(
        channel = channel.get_channel(),
        force_push_slack=force_push_slack.get_bool();
        "{}", get_message(summary, details)
    );
}

#[pyfunction]
fn error(
    summary: &PyString,
    details: Option<&PyString>,
    channel: Option<&PyString>,
    force_push_slack: Option<bool>,
) {
    error!(
        channel = channel.get_channel(),
        force_push_slack=force_push_slack.get_bool();
        "{}", get_message(summary, details)
    );
}

#[pyfunction]
fn debug(
    summary: &PyString,
    details: Option<&PyString>,
    channel: Option<&PyString>,
    force_push_slack: Option<bool>,
) {
    debug!(
        channel = channel.get_channel(),
        force_push_slack=force_push_slack.get_bool();
        "{}", get_message(summary, details)
    );
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
fn enable_slack(slack_token: &PyString) {
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
fn log_to_file(log_file: &PyString) {
    STATE
        .lock()
        .unwrap()
        .set_log_file(Some(log_file.to_string()));
}

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
    m.add_function(wrap_pyfunction!(enable_slack, m)?)?;
    m.add_function(wrap_pyfunction!(set_slack_level, m)?)?;
    m.add_function(wrap_pyfunction!(log_to_file, m)?)?;
    m.add_function(wrap_pyfunction!(tpl, m)?)?;
    Ok(())
}
