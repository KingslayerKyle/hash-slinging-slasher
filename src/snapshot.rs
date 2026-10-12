//! The set of asset ids a game holds, as a file that outlives the loader.
//!
//! This is the whole reason someone without the game can take part. Confirming a name asks one
//! question -- is this hash the id of an asset the game holds -- and that question is answered
//! by a set of numbers, not by the game. Captured once by someone running Cordycep, the set
//! travels: any machine, any platform, no loader, no install.
//!
//! The format is deliberately dull. Ids are stored sorted so a lookup is a binary search over a
//! memory mapped slice rather than a hash map that has to be built first, and a record carries
//! the pool it was found in so a confirmed name can be filed by type. An id held in several
//! pools is several records, which is how a model that also has a skeleton and a collision comes
//! back as all three.

use std::fs;
use std::io;
use std::path::Path;

/// Magic and version. The version is here so a reader that predates a format change refuses the
/// file rather than reading it wrongly, which for a file of raw numbers it otherwise would.
const MAGIC: &[u8; 6] = b"CODIDS";
const VERSION: u16 = 1;

/// One asset: the id the loader holds it under, and the pool index it sits in.
pub type Record = (u64, u16);

/// Bytes per record on disk: eight for the id, two for the pool.
const RECORD: usize = 10;

/// Writes a snapshot, returning how many bytes it came to.
///
/// Sorted and deduplicated here rather than trusted from the caller. The reader binary searches
/// these records, so an unsorted file is not a file that fails -- it is a file that quietly
/// answers "the game does not hold that" for names the game does hold. That failure is invisible
/// and would be inherited by everyone grinding against the snapshot, which is worth one sort.
pub fn write(
    path: &Path,
    game: &str,
    records: impl Iterator<Item = Record>,
) -> io::Result<usize> {
    let mut records: Vec<Record> = records.collect();
    records.sort_unstable();
    records.dedup();

    let mut bytes = Vec::with_capacity(16 + game.len() + records.len() * RECORD);
    bytes.extend_from_slice(MAGIC);
    bytes.extend_from_slice(&VERSION.to_le_bytes());
    bytes.extend_from_slice(&(game.len() as u16).to_le_bytes());
    bytes.extend_from_slice(game.as_bytes());
    bytes.extend_from_slice(&(records.len() as u64).to_le_bytes());

    for (id, pool) in &records {
        bytes.extend_from_slice(&id.to_le_bytes());
        bytes.extend_from_slice(&pool.to_le_bytes());
    }

    fs::write(path, &bytes)?;

    Ok(bytes.len())
}

/// A snapshot read back: which game it came from, and every asset it holds.
pub struct Snapshot {
    game: String,
    records: Vec<Record>,
}

impl Snapshot {
    pub fn read(path: &Path) -> io::Result<Self> {
        let bytes = fs::read(path)?;
        Self::parse(&bytes)
    }

    fn parse(bytes: &[u8]) -> io::Result<Self> {
        let bad = |what: &str| io::Error::new(io::ErrorKind::InvalidData, what.to_owned());

        if bytes.len() < 16 || &bytes[0..6] != MAGIC {
            return Err(bad("not a snapshot file"));
        }

        let version = u16::from_le_bytes([bytes[6], bytes[7]]);
        if version != VERSION {
            return Err(bad(&format!(
                "snapshot is version {version}, this reads version {VERSION}"
            )));
        }

        let name_len = u16::from_le_bytes([bytes[8], bytes[9]]) as usize;
        let mut at = 10;

        if bytes.len() < at + name_len + 8 {
            return Err(bad("snapshot header is truncated"));
        }

        let game = String::from_utf8_lossy(&bytes[at..at + name_len]).into_owned();
        at += name_len;

        let count = u64::from_le_bytes(
            bytes[at..at + 8].try_into().map_err(|_| bad("bad count"))?,
        );
        let count = usize::try_from(count).map_err(|_| bad("snapshot record count is too large"))?;
        at += 8;

        let end = count
            .checked_mul(RECORD)
            .and_then(|size| at.checked_add(size))
            .ok_or_else(|| bad("snapshot record count is too large"))?;
        if bytes.len() != end {
            return Err(bad("snapshot payload length does not match its record count"));
        }

        let mut records = Vec::with_capacity(count);
        for index in 0..count {
            let start = at + index * RECORD;
            let id = u64::from_le_bytes(
                bytes[start..start + 8].try_into().map_err(|_| bad("bad id"))?,
            );
            let pool = u16::from_le_bytes([bytes[start + 8], bytes[start + 9]]);
            if records.last().is_some_and(|(previous, _)| *previous > id) {
                return Err(bad("snapshot ids are not sorted"));
            }
            records.push((id, pool));
        }

        Ok(Self { game, records })
    }

    /// The game this was captured from. Checked before a search runs, so one game's names can
    /// never be confirmed against another's assets.
    pub fn game(&self) -> &str {
        &self.game
    }

    pub fn len(&self) -> usize {
        self.records.len()
    }

    pub fn is_empty(&self) -> bool {
        self.records.is_empty()
    }

    /// Every pool an id is held in, which is empty when the game does not hold it at all.
    ///
    /// A binary search over the sorted records, then a walk either side of the hit, since an id
    /// in several pools is several adjacent records.
    pub fn pools_of(&self, id: u64) -> &[Record] {
        let start = self.records.partition_point(|(held, _)| *held < id);
        let end = start + self.records[start..].partition_point(|(held, _)| *held == id);

        &self.records[start..end]
    }

    /// Whether the game holds this id at all.
    pub fn holds(&self, id: u64) -> bool {
        self.records.binary_search_by_key(&id, |(held, _)| *held).is_ok()
    }

    /// Every distinct id, for building a filter over.
    pub fn ids(&self) -> impl Iterator<Item = u64> + '_ {
        self.records.iter().map(|(id, _)| *id)
    }

    /// Every id with the pool it is held in, which is what a search wants: the id is the evidence
    /// and the pool is what says which kind of name it could be. An id in several pools appears
    /// once per pool, in id order.
    pub fn records(&self) -> impl Iterator<Item = Record> + '_ {
        self.records.iter().copied()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn encoded_snapshot(count: u64, records: &[Record]) -> Vec<u8> {
        let mut bytes = Vec::new();
        bytes.extend_from_slice(MAGIC);
        bytes.extend_from_slice(&VERSION.to_le_bytes());
        bytes.extend_from_slice(&8u16.to_le_bytes());
        bytes.extend_from_slice(b"BLKOPSCW");
        bytes.extend_from_slice(&count.to_le_bytes());
        for (id, pool) in records {
            bytes.extend_from_slice(&id.to_le_bytes());
            bytes.extend_from_slice(&pool.to_le_bytes());
        }
        bytes
    }

    #[test]
    fn an_oversized_record_count_is_refused_without_panicking() {
        for count in [u64::MAX, u64::MAX / RECORD as u64] {
            let error = Snapshot::parse(&encoded_snapshot(count, &[]))
                .err()
                .expect("an impossible record count must be refused");
            assert_eq!(error.kind(), io::ErrorKind::InvalidData);
        }
    }

    #[test]
    fn records_not_claimed_by_the_header_are_refused() {
        let error = Snapshot::parse(&encoded_snapshot(0, &[(1, 6)]))
            .err()
            .expect("a payload inconsistent with its count must be refused");
        assert_eq!(error.kind(), io::ErrorKind::InvalidData);
    }

    #[test]
    fn unsorted_ids_are_refused_before_a_lookup_can_miss_them() {
        let error = Snapshot::parse(&encoded_snapshot(3, &[(3, 6), (2, 6), (1, 6)]))
            .err()
            .expect("binary search requires ids in ascending order");
        assert_eq!(error.kind(), io::ErrorKind::InvalidData);
    }

    #[test]
    fn sorted_ids_keep_every_pool_even_without_canonical_pool_order() {
        let records = [(1, 8), (1, 6), (1, 6), (2, 10)];
        let snapshot = Snapshot::parse(&encoded_snapshot(records.len() as u64, &records)).unwrap();
        assert_eq!(snapshot.pools_of(1), &records[..3]);
        assert!(snapshot.holds(2));
    }

    fn round_trip(game: &str, records: Vec<Record>) -> Snapshot {
        let dir = std::env::temp_dir().join(format!("snap_{}_{}", std::process::id(), game));
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.ids");

        write(&path, game, records.into_iter()).unwrap();
        let read = Snapshot::read(&path).unwrap();

        let _ = fs::remove_dir_all(&dir);
        read
    }

    #[test]
    fn a_snapshot_survives_the_round_trip() {
        let snap = round_trip("BLKOPSCW", vec![(1, 6), (2, 10), (9_000_000_000, 184)]);

        assert_eq!(snap.game(), "BLKOPSCW");
        assert_eq!(snap.len(), 3);
        assert!(snap.holds(9_000_000_000));
        assert!(!snap.holds(3));
    }

    /// An id held in several pools comes back as all of them, which is how a model that also has
    /// a skeleton and a collision is recognised as all three.
    #[test]
    fn an_id_in_several_pools_returns_every_one() {
        let snap = round_trip("T9", vec![(5, 6), (5, 8), (5, 7), (6, 10)]);

        let pools: Vec<u16> = snap.pools_of(5).iter().map(|(_, pool)| *pool).collect();

        assert_eq!(pools, vec![6, 7, 8]);
        assert_eq!(snap.pools_of(6).len(), 1);
        assert!(snap.pools_of(99).is_empty());
    }

    /// The game is recorded in the file, so a snapshot cannot be mistaken for another game's.
    #[test]
    fn the_game_is_carried_by_the_file() {
        assert_eq!(round_trip("BO4", vec![(1, 1)]).game(), "BO4");
    }

    #[test]
    fn a_file_that_is_not_a_snapshot_is_refused() {
        assert!(Snapshot::parse(b"hello there, not a snapshot").is_err());
    }

    #[test]
    fn a_truncated_snapshot_is_refused_rather_than_half_read() {
        let dir = std::env::temp_dir().join(format!("snap_trunc_{}", std::process::id()));
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("t.ids");
        write(&path, "T9", vec![(1, 1), (2, 2), (3, 3)].into_iter()).unwrap();

        let mut bytes = fs::read(&path).unwrap();
        bytes.truncate(bytes.len() - 5);

        assert!(Snapshot::parse(&bytes).is_err());

        let _ = fs::remove_dir_all(&dir);
    }
}
